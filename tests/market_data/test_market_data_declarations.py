from __future__ import annotations

from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.market_data import (
    AvailabilityPolicy,
    MarketDataAvailabilityError,
    MarketDataBundle,
    MarketDataDeclaration,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
)


class FakeCalendar:
    def __init__(self) -> None:
        self.sessions = pd.DatetimeIndex(
            pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06"])
        )

    def sessions_in_range(self, start: date, end: date) -> pd.DatetimeIndex:
        return self.sessions[
            (self.sessions >= pd.Timestamp(start)) & (self.sessions <= pd.Timestamp(end))
        ]

    def session_on_or_before(self, value: date) -> date:
        return self.sessions[self.sessions <= pd.Timestamp(value)][-1].date()

    def session_on_or_after(self, value: date) -> date:
        return self.sessions[self.sessions >= pd.Timestamp(value)][0].date()

    def session_offset(self, value: date, offset: int) -> date:
        position = self.sessions.get_loc(pd.Timestamp(value))
        return self.sessions[position + offset].date()

    def session_distance(self, older: date, newer: date) -> int:
        older_position = self.sessions.get_loc(pd.Timestamp(self.session_on_or_before(older)))
        newer_position = self.sessions.get_loc(pd.Timestamp(self.session_on_or_before(newer)))
        return newer_position - older_position

    def decision_time(self, session: date) -> datetime:
        return datetime(session.year, session.month, session.day, 20, 30, tzinfo=UTC)


def bars(closes: list[float]) -> pd.DataFrame:
    dates = pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06"])
    close = pd.Series(closes, index=dates)
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 1,
            "Low": close - 1,
            "Close": close,
            "Volume": 100.0,
        }
    )


def requirement(symbol: str, role: str) -> MarketDataRequirement:
    return MarketDataRequirement(
        MarketDataSeries.yahoo_adjusted_daily(symbol),
        date(2026, 8, 3),
        role=role,
        availability_policy=AvailabilityPolicy() if role == "auxiliary" else None,
    )


def test_declaration_requires_exactly_one_primary_series() -> None:
    with pytest.raises(ValueError, match="exactly one primary"):
        MarketDataDeclaration.from_requirements((requirement("^VIX", "auxiliary"),))

    with pytest.raises(ValueError, match="exactly one primary"):
        MarketDataDeclaration.from_requirements(
            (requirement("SPY", "primary"), requirement("QQQ", "primary"))
        )


def test_declaration_exposes_primary_and_auxiliary_roles() -> None:
    declaration = MarketDataDeclaration.from_requirements(
        (requirement("SPY", "primary"), requirement("^VIX", "auxiliary"))
    )

    assert declaration.primary.series.symbol == "SPY"
    assert tuple(item.series.symbol for item in declaration.auxiliary) == ("^VIX",)
    assert declaration.requirements == (
        requirement("SPY", "primary"),
        requirement("^VIX", "auxiliary"),
    )


def test_bundle_requirement_validation_rejects_missing_or_multiple_primary_series() -> None:
    with pytest.raises(MarketDataAvailabilityError, match="exactly one primary"):
        MarketDataBundle.validate_requirements((requirement("^VIX", "auxiliary"),))

    with pytest.raises(MarketDataAvailabilityError, match="exactly one primary"):
        MarketDataBundle.validate_requirements(
            (requirement("SPY", "primary"), requirement("QQQ", "primary"))
        )


def test_bundle_aligns_auxiliary_for_every_primary_decision_session() -> None:
    calendar = FakeCalendar()
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    requirements = (
        MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
        MarketDataRequirement(
            auxiliary,
            date(2026, 8, 3),
            role="auxiliary",
            availability_policy=AvailabilityPolicy(
                publication_lag_sessions=1,
                max_observation_lag_sessions=2,
                publication_time_known=False,
            ),
        ),
    )
    decisions = tuple(
        SignalDecisionTime.for_primary_session(session, calendar=calendar)
        for session in (date(2026, 8, 4), date(2026, 8, 5), date(2026, 8, 6))
    )

    bundle = MarketDataBundle.from_requirements(
        requirements,
        {primary: bars([100.0, 101.0, 102.0, 103.0]), auxiliary: bars([10.0, 20.0, 30.0, 40.0])},
        decision_time=decisions[-1],
        decision_times=decisions,
        calendar=calendar,
    )

    aligned = bundle[auxiliary]
    assert bundle.declaration.primary.series == primary
    assert bundle.decision_times == decisions
    assert list(aligned.index.strftime("%Y-%m-%d")) == ["2026-08-04", "2026-08-05", "2026-08-06"]
    assert list(aligned["Close"]) == [10.0, 20.0, 30.0]
    assert list(aligned["ObservationDate"].dt.strftime("%Y-%m-%d")) == [
        "2026-08-03",
        "2026-08-04",
        "2026-08-05",
    ]


def test_bundle_rejects_non_chronological_decision_sessions() -> None:
    calendar = FakeCalendar()
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    decisions = tuple(
        SignalDecisionTime.for_primary_session(session, calendar=calendar)
        for session in (date(2026, 8, 5), date(2026, 8, 4))
    )

    with pytest.raises(MarketDataAvailabilityError, match="chronological"):
        MarketDataBundle.from_requirements(
            (MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),),
            {primary: bars([100.0, 101.0, 102.0, 103.0])},
            decision_time=decisions[-1],
            decision_times=decisions,
            calendar=calendar,
        )
