from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.market_data import (
    AvailabilityPolicy,
    CacheCorruptionError,
    CoverageMode,
    CsvMarketDataCache,
    MarketDataBundle,
    MarketDataCoveragePolicy,
    MarketDataRequirement,
    MarketDataSeries,
    RefreshKind,
    SignalDecisionTime,
)
from trading.research_data import ResearchDataStore


def bars(dates: list[str], closes: list[float]) -> pd.DataFrame:
    close = pd.Series(closes, index=pd.to_datetime(dates))
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 1,
            "Low": close - 1,
            "Close": close,
            "Volume": 100.0,
        }
    )


def test_coverage_policy_distinguishes_primary_sessions_from_sparse_observations() -> None:
    assert MarketDataCoveragePolicy.xnys().mode is CoverageMode.XNYS_SESSIONS
    assert (
        MarketDataCoveragePolicy.provider_observations().mode is CoverageMode.PROVIDER_OBSERVATIONS
    )

    with pytest.raises(ValueError, match="primary series require XNYS"):
        MarketDataRequirement(
            MarketDataSeries.yahoo_adjusted_daily("SPY"),
            date(2026, 8, 3),
            role="primary",
            coverage_policy=MarketDataCoveragePolicy.provider_observations(),
        )


def test_bundle_accepts_sparse_auxiliary_observation_coverage() -> None:
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("EURUSD=X")
    requirements = (
        MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
        MarketDataRequirement(
            auxiliary,
            date(2026, 8, 3),
            role="auxiliary",
            availability_policy=AvailabilityPolicy(max_observation_lag_sessions=2),
            coverage_policy=MarketDataCoveragePolicy.provider_observations(),
        ),
    )

    bundle = MarketDataBundle.from_requirements(
        requirements,
        {
            primary: bars(
                ["2026-08-03", "2026-08-04", "2026-08-05"],
                [100.0, 101.0, 102.0],
            ),
            auxiliary: bars(["2026-08-03", "2026-08-05"], [1.0, 3.0]),
        },
        decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 5)),
    )

    aligned = bundle[auxiliary]
    assert list(aligned["Close"]) == [1.0]


def test_cache_persists_and_validates_sparse_observation_coverage(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("EURUSD=X")
    policy = MarketDataCoveragePolicy.provider_observations()
    source = bars(["2026-08-03", "2026-08-05"], [1.0, 3.0])

    published = cache.publish(
        series,
        source,
        refresh_kind="full",
        refreshed_at=datetime(2026, 8, 6, tzinfo=UTC),
        coverage_policy=policy,
    )
    loaded = cache.load(series, coverage_policy=policy)

    assert loaded is not None
    assert loaded.metadata.coverage_policy == CoverageMode.PROVIDER_OBSERVATIONS.value
    pd.testing.assert_frame_equal(loaded.bars, published.bars, check_freq=False)

    with pytest.raises(CacheCorruptionError, match="coverage policy"):
        cache.load(series)


def test_snapshot_manifest_round_trips_sparse_coverage_without_requiring_xnys_gaps(
    tmp_path,
) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("EURUSD=X")
    primary_frame = bars(
        ["2026-08-03", "2026-08-04", "2026-08-05"],
        [100.0, 101.0, 102.0],
    )
    # A one-session publication lag requires an observation before the first
    # primary decision; the snapshot loader must preserve that earliest
    # decision instead of silently dropping it.
    auxiliary_frame = bars(["2026-07-31", "2026-08-03", "2026-08-04"], [0.0, 1.0, 2.0])
    cache.publish(
        primary,
        primary_frame,
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 6, tzinfo=UTC),
    )
    sparse_policy = MarketDataCoveragePolicy.provider_observations()
    cache.publish(
        auxiliary,
        auxiliary_frame,
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 6, tzinfo=UTC),
        coverage_policy=sparse_policy,
    )
    requirements = (
        MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
        MarketDataRequirement(
            auxiliary,
            date(2026, 8, 3),
            role="auxiliary",
            availability_policy=AvailabilityPolicy(max_observation_lag_sessions=2),
            coverage_policy=sparse_policy,
        ),
    )
    store = ResearchDataStore(
        tmp_path / "research-data",
        now=lambda: datetime(2026, 8, 6, 12, tzinfo=UTC),
    )
    decision_time = SignalDecisionTime.for_primary_session(date(2026, 8, 5))

    manifest = store.create_snapshot(cache, requirements, decision_time)
    manifest_path = store.write_manifest(manifest, tmp_path / "run.snapshot.json")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest.data[1].coverage_policy == sparse_policy
    assert payload["data"][0].get("coverage_policy") is None
    assert payload["data"][1]["coverage_policy"] == CoverageMode.PROVIDER_OBSERVATIONS.value
    loaded = ResearchDataStore(tmp_path / "research-data").load_snapshot(manifest_path)
    assert loaded.manifest == manifest
    assert list(loaded.bundle[auxiliary]["ObservationDate"]) == [
        pd.Timestamp("2026-07-31"),
        pd.Timestamp("2026-08-03"),
        pd.Timestamp("2026-08-04"),
    ]
