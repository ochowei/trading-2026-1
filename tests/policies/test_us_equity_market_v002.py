from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.market_data import (
    AvailabilityPolicy,
    MarketDataAvailabilityError,
    MarketDataCoveragePolicy,
    MarketDataSeries,
    SignalDecisionTime,
    align_auxiliary,
)
from trading.market_data.availability import (
    ExcessObservationLagMode,
    GapAwareAvailabilityPolicy,
)
from trading.research_data.manifest_codec import (
    canonical_json_bytes,
    manifest_body,
    manifest_from_bytes,
    manifest_payload,
)
from trading.research_data.models import DataBlobRef, SnapshotDataRef, SnapshotManifest


class WeekdayCalendar:
    def session_on_or_after(self, session: date) -> date:
        return session

    def session_offset(self, session: date, offset: int) -> date:
        return (pd.Timestamp(session) + pd.offsets.BDay(offset)).date()

    def session_distance(self, start: date, end: date) -> int:
        return len(pd.bdate_range(start, end)) - 1


def _bar() -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [10.0], "High": [11.0], "Low": [9.0], "Close": [10.0], "Volume": [100.0]},
        index=pd.to_datetime(["2026-08-03"]),
    )


def test_us_equity_market_v002_keeps_fail_default_and_marks_explicit_unavailability() -> None:
    default = AvailabilityPolicy(
        publication_lag_sessions=1,
        max_observation_lag_sessions=2,
        publication_time_known=False,
    )
    gap_aware = GapAwareAvailabilityPolicy(
        publication_lag_sessions=1,
        max_observation_lag_sessions=2,
        publication_time_known=False,
    )

    decision = SignalDecisionTime.for_primary_session(date(2026, 8, 6))
    with pytest.raises(MarketDataAvailabilityError, match="maximum observation lag"):
        align_auxiliary([decision], _bar(), policy=default, calendar=WeekdayCalendar())
    aligned = align_auxiliary([decision], _bar(), policy=gap_aware, calendar=WeekdayCalendar())

    assert not hasattr(default, "excess_lag_mode")
    assert gap_aware.excess_lag_mode is ExcessObservationLagMode.MARK_UNAVAILABLE
    assert aligned.iloc[0]["ObservationLagSessions"] == 3
    assert aligned.iloc[0]["ObservationAvailable"] == False  # noqa: E712
    assert aligned.iloc[0]["Close"] == 10.0


def test_us_equity_market_v002_round_trips_non_default_manifest_mode() -> None:
    policy = GapAwareAvailabilityPolicy(
        publication_lag_sessions=1,
        max_observation_lag_sessions=3,
        publication_time_known=False,
    )
    created_at = datetime(2026, 8, 12, tzinfo=UTC)
    decision = SignalDecisionTime.for_primary_session(date(2026, 8, 11))
    entries = (
        SnapshotDataRef(
            series=MarketDataSeries.yahoo_adjusted_daily("^MOVE"),
            history_start=date(2002, 11, 13),
            role="auxiliary",
            availability_policy=policy,
            data_cutoff=date(2026, 8, 11),
            full_refresh_at=created_at,
            blob=DataBlobRef("a" * 64, 1, 1),
            coverage_policy=MarketDataCoveragePolicy.provider_observations(),
        ),
    )
    body = manifest_body(created_at, decision, entries, None)
    snapshot_id = __import__("hashlib").sha256(canonical_json_bytes(body)).hexdigest()
    manifest = SnapshotManifest(
        snapshot_id=snapshot_id,
        schema_version=1,
        created_at=created_at,
        decision_time=decision,
        data=entries,
    )
    content = canonical_json_bytes(manifest_payload(manifest))

    replayed = manifest_from_bytes(content)

    assert body["data"][0]["availability_policy"]["excess_lag_mode"] == "mark_unavailable"
    assert isinstance(replayed.data[0].availability_policy, GapAwareAvailabilityPolicy)
    assert (
        replayed.data[0].availability_policy.excess_lag_mode
        is ExcessObservationLagMode.MARK_UNAVAILABLE
    )
