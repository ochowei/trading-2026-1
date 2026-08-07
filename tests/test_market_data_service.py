from __future__ import annotations

import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.market_data import (
    AvailabilityPolicy,
    CoverageMode,
    CsvMarketDataCache,
    MarketDataAvailabilityError,
    MarketDataCoveragePolicy,
    MarketDataRequirement,
    MarketDataSeries,
    MarketDataService,
    MarketDataUnavailableError,
    MarketDataValidationError,
    SignalDecisionTime,
)


class FakeCalendar:
    def __init__(self, sessions: list[str], latest: str):
        self.sessions = pd.DatetimeIndex(pd.to_datetime(sessions))
        self.latest = pd.Timestamp(latest)

    def latest_completed_session(self, now: datetime) -> date:
        return self.latest.date()

    def sessions_in_range(self, start: date, end: date) -> pd.DatetimeIndex:
        return self.sessions[
            (self.sessions >= pd.Timestamp(start)) & (self.sessions <= pd.Timestamp(end))
        ]

    def session_on_or_before(self, value: date) -> date:
        return self.sessions[self.sessions <= pd.Timestamp(value)][-1].date()

    def session_on_or_after(self, value: date) -> date:
        return self.sessions[self.sessions >= pd.Timestamp(value)][0].date()

    def session_offset(self, value: date, offset: int) -> date:
        location = self.sessions.get_loc(pd.Timestamp(value))
        return self.sessions[location + offset].date()

    def session_distance(self, older: date, newer: date) -> int:
        older_location = self.sessions.get_loc(pd.Timestamp(self.session_on_or_before(older)))
        newer_location = self.sessions.get_loc(pd.Timestamp(self.session_on_or_before(newer)))
        return newer_location - older_location


class FakeProvider:
    def __init__(self, frame: pd.DataFrame, delay: float = 0):
        self.frame = frame
        self.delay = delay
        self.calls: list[tuple[date | None, date]] = []
        self._guard = threading.Lock()

    def fetch(self, series, *, start: date | None, end: date) -> pd.DataFrame:
        with self._guard:
            self.calls.append((start, end))
        if self.delay:
            time.sleep(self.delay)
        result = self.frame.loc[: pd.Timestamp(end)]
        if start is not None:
            result = result.loc[pd.Timestamp(start) :]
        return result.copy()


def bars() -> pd.DataFrame:
    dates = pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06"])
    close = pd.Series([10.0, 11.0, 12.0, 13.0], index=dates)
    return pd.DataFrame(
        {
            "Open": close - 0.5,
            "High": close + 1,
            "Low": close - 1,
            "Close": close,
            "Volume": 100.0,
        }
    )


def service(tmp_path, provider, calendar) -> MarketDataService:
    return MarketDataService(
        provider=provider,
        cache=CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine"),
        calendar=calendar,
        now=lambda: datetime(2026, 8, 7, tzinfo=UTC),
        incremental_overlap_sessions=2,
    )


def test_fresh_series_is_reused_without_network(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")

    first = market_data.get(series, start=date(2026, 8, 3))
    second = market_data.get(series, start=date(2026, 8, 3))

    assert provider.calls == [(date(2026, 8, 3), date(2026, 8, 4))]
    pd.testing.assert_frame_equal(first, second)


def test_status_reports_stale_without_network_or_cache_mutation(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        "2026-08-04",
    )
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    market_data.get(series, start=date(2026, 8, 3))
    provider.calls.clear()
    before = set(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    calendar.latest = pd.Timestamp("2026-08-05")

    inspection = market_data.status(series)

    assert inspection.state == "stale"
    assert provider.calls == []
    assert set(path.relative_to(tmp_path) for path in tmp_path.rglob("*")) == before


def test_status_reports_busy_during_refresh_without_mutation(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars())
    cache = CsvMarketDataCache(
        tmp_path / "active",
        tmp_path / "quarantine",
        lock_timeout_seconds=0.02,
        lock_poll_seconds=0.005,
    )
    market_data = MarketDataService(
        provider=provider,
        cache=cache,
        calendar=calendar,
        now=lambda: datetime(2026, 8, 7, tzinfo=UTC),
    )
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    market_data.get(series, start=date(2026, 8, 3))
    before = set(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    with cache.lock(series), ThreadPoolExecutor(max_workers=1) as executor:
        inspection = executor.submit(market_data.status, series).result()

    assert inspection.state == "busy"
    assert set(path.relative_to(tmp_path) for path in tmp_path.rglob("*")) == before


def test_incremental_refresh_fetches_only_missing_range_and_overlap(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06"],
        "2026-08-04",
    )
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    market_data.get(series, start=date(2026, 8, 3))

    calendar.latest = pd.Timestamp("2026-08-06")
    refreshed = market_data.get(series, start=date(2026, 8, 3))

    assert provider.calls[-1] == (date(2026, 8, 3), date(2026, 8, 6))
    assert list(refreshed.index) == list(calendar.sessions)


def test_full_refresh_replaces_entire_series_and_marks_it_complete(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")

    market_data.refresh(series, mode="full")
    cached = market_data.cache.load(series)

    assert provider.calls == [(None, date(2026, 8, 4))]
    assert cached is not None
    assert cached.metadata.last_complete_refresh == datetime(2026, 8, 7, tzinfo=UTC)


def test_full_refresh_rejects_a_partial_history_start(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)

    with pytest.raises(ValueError, match="does not accept start"):
        market_data.refresh(
            MarketDataSeries.yahoo_adjusted_daily("SPY"),
            mode="full",
            start=date(2026, 8, 3),
        )

    assert provider.calls == []


def test_explicit_refresh_cannot_regress_active_data_cutoff(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        "2026-08-05",
    )
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    market_data.get(series, start=date(2026, 8, 3))
    provider.calls.clear()

    with pytest.raises(MarketDataUnavailableError, match="precedes active cache cutoff"):
        market_data.refresh(series, mode="full", end=date(2026, 8, 4))

    assert provider.calls == []
    active = market_data.cache.load(series)
    assert active is not None
    assert active.metadata.data_cutoff == date(2026, 8, 5)


def test_corrupt_cache_is_quarantined_and_fully_rebuilt(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    market_data.get(series, start=date(2026, 8, 3))
    market_data.cache.paths(series).csv.write_text("corrupt")

    rebuilt = market_data.get(series, start=date(2026, 8, 3))

    assert len(rebuilt) == 2
    assert provider.calls[-1] == (None, date(2026, 8, 4))
    assert list((tmp_path / "quarantine").rglob("*.csv"))


def test_cache_missing_a_primary_session_is_quarantined_and_rebuilt(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        "2026-08-05",
    )
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    market_data.get(series, start=date(2026, 8, 3))
    provider.calls.clear()
    paths = market_data.cache.paths(series)
    incomplete = bars().loc[pd.to_datetime(["2026-08-03", "2026-08-05"])]
    csv_bytes = incomplete.to_csv(
        index=True,
        index_label="Date",
        date_format="%Y-%m-%d",
        float_format="%.17g",
        lineterminator="\n",
    ).encode("utf-8")
    paths.csv.write_bytes(csv_bytes)
    metadata = json.loads(paths.metadata.read_text())
    metadata["checksum"] = hashlib.sha256(csv_bytes).hexdigest()
    paths.metadata.write_text(
        json.dumps(metadata, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    rebuilt = market_data.get(series, start=date(2026, 8, 3))

    assert len(rebuilt) == 3
    assert provider.calls == [(None, date(2026, 8, 5))]
    assert list((tmp_path / "quarantine").rglob("*.csv"))


def test_invalid_refresh_never_replaces_valid_active_cache(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        "2026-08-04",
    )
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    original = market_data.get(series, start=date(2026, 8, 3))
    calendar.latest = pd.Timestamp("2026-08-05")
    provider.frame.loc[pd.Timestamp("2026-08-05"), "Volume"] = -1

    with pytest.raises(MarketDataValidationError, match="negative volume"):
        market_data.get(series, start=date(2026, 8, 3))

    active = market_data.cache.load(series)
    assert active is not None
    pd.testing.assert_frame_equal(active.bars, original)


def test_concurrent_refresh_publishes_once(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars(), delay=0.1)
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")

    with ThreadPoolExecutor(max_workers=2) as executor:
        frames = list(
            executor.map(
                lambda _: market_data.get(series, start=date(2026, 8, 3)),
                range(2),
            )
        )

    assert len(provider.calls) == 1
    pd.testing.assert_frame_equal(frames[0], frames[1])
    assert market_data.cache.load(series) is not None


def test_concurrent_explicit_incremental_refresh_downloads_once(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars(), delay=0.1)
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")

    with ThreadPoolExecutor(max_workers=2) as executor:
        frames = list(
            executor.map(
                lambda _: market_data.refresh(
                    series,
                    mode="incremental",
                    start=date(2026, 8, 3),
                ),
                range(2),
            )
        )

    assert len(provider.calls) == 1
    pd.testing.assert_frame_equal(frames[0], frames[1])


def test_service_builds_complete_bundle_from_declared_requirements(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        "2026-08-04",
    )
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    requirements = (
        MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
        MarketDataRequirement(
            auxiliary,
            date(2026, 8, 3),
            role="auxiliary",
            availability_policy=AvailabilityPolicy(1, 1, False),
        ),
    )

    bundle = market_data.build_bundle(
        requirements,
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )

    assert set(bundle) == {primary, auxiliary}
    assert len(provider.calls) == 2
    assert all(call == (date(2026, 8, 3), date(2026, 8, 4)) for call in provider.calls)


def test_service_builds_historical_auxiliary_rows_for_requested_decisions(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        "2026-08-05",
    )
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    requirements = (
        MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
        MarketDataRequirement(
            auxiliary,
            date(2026, 8, 3),
            role="auxiliary",
            availability_policy=AvailabilityPolicy(1, 2, False),
        ),
    )
    decisions = (
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        SignalDecisionTime.for_primary_session(date(2026, 8, 5)),
    )

    bundle = market_data.build_bundle(
        requirements,
        decisions[-1],
        decision_times=decisions,
    )

    assert list(bundle[auxiliary].index) == list(pd.to_datetime(["2026-08-04", "2026-08-05"]))
    assert list(bundle[auxiliary]["ObservationDate"]) == list(
        pd.to_datetime(["2026-08-03", "2026-08-04"])
    )


def test_provider_observation_coverage_allows_a_valid_gap_at_requested_cutoff(tmp_path) -> None:
    calendar = FakeCalendar(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        "2026-08-05",
    )
    provider = FakeProvider(bars().loc[pd.to_datetime(["2026-08-03", "2026-08-04"])])
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("EURUSD=X")
    policy = MarketDataCoveragePolicy.provider_observations()

    resolved = market_data.get(
        series,
        start=date(2026, 8, 3),
        coverage_policy=policy,
    )

    assert list(resolved.index) == list(pd.to_datetime(["2026-08-03", "2026-08-04"]))
    cached = market_data.cache.load(series, coverage_policy=policy)
    assert cached is not None
    assert cached.metadata.coverage_policy == CoverageMode.PROVIDER_OBSERVATIONS.value
    assert cached.metadata.data_cutoff == date(2026, 8, 4)


def test_bundle_requirement_errors_fail_before_provider_access(tmp_path) -> None:
    calendar = FakeCalendar(["2026-08-03", "2026-08-04"], "2026-08-04")
    provider = FakeProvider(bars())
    market_data = service(tmp_path, provider, calendar)
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    requirement = MarketDataRequirement(series, date(2026, 8, 3), role="primary")

    with pytest.raises(MarketDataAvailabilityError, match="declared more than once"):
        market_data.build_bundle(
            (requirement, requirement),
            SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        )

    assert provider.calls == []
