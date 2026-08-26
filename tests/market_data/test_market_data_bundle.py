from datetime import date

import pandas as pd
import pytest

from trading.market_data import (
    AvailabilityPolicy,
    MarketDataAvailabilityError,
    MarketDataBundle,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
    align_auxiliary,
)
from trading.market_data.availability import GapAwareAvailabilityPolicy


class FakeCalendar:
    def __init__(self):
        self.sessions = pd.DatetimeIndex(
            pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06"])
        )

    def sessions_in_range(self, start, end):
        return self.sessions[
            (self.sessions >= pd.Timestamp(start)) & (self.sessions <= pd.Timestamp(end))
        ]

    def session_on_or_before(self, value):
        return self.sessions[self.sessions <= pd.Timestamp(value)][-1].date()

    def session_on_or_after(self, value):
        return self.sessions[self.sessions >= pd.Timestamp(value)][0].date()

    def session_offset(self, value, offset):
        anchor = self.sessions.get_loc(pd.Timestamp(value))
        return self.sessions[anchor + offset].date()

    def session_distance(self, older, newer):
        return self.sessions.get_loc(pd.Timestamp(newer)) - self.sessions.get_loc(
            pd.Timestamp(self.session_on_or_before(older))
        )


def frame(dates: list[str], closes: list[float]) -> pd.DataFrame:
    index = pd.to_datetime(dates)
    close = pd.Series(closes, index=index)
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 1,
            "Low": close - 1,
            "Close": close,
            "Volume": 100.0,
        }
    )


def test_unknown_publication_time_requires_conservative_lag() -> None:
    with pytest.raises(ValueError, match="at least one session"):
        AvailabilityPolicy(
            publication_lag_sessions=0,
            max_observation_lag_sessions=2,
            publication_time_known=False,
        )

    with pytest.raises(ValueError, match="cannot be shorter"):
        AvailabilityPolicy(
            publication_lag_sessions=2,
            max_observation_lag_sessions=1,
            publication_time_known=True,
        )


def test_auxiliary_alignment_is_backward_as_of_information_availability() -> None:
    calendar = FakeCalendar()
    auxiliary = frame(["2026-08-03", "2026-08-04"], [10.0, 20.0])
    decisions = [
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        SignalDecisionTime.for_primary_session(date(2026, 8, 5)),
    ]
    policy = AvailabilityPolicy(
        publication_lag_sessions=1,
        max_observation_lag_sessions=2,
        publication_time_known=False,
    )

    aligned = align_auxiliary(decisions, auxiliary, policy=policy, calendar=calendar)

    assert list(aligned["ObservationDate"].dt.strftime("%Y-%m-%d")) == [
        "2026-08-03",
        "2026-08-04",
    ]
    assert list(aligned["Close"]) == [10.0, 20.0]
    assert list(aligned["ObservationLagSessions"]) == [1, 1]


def test_auxiliary_alignment_fails_closed_when_observation_lag_is_excessive() -> None:
    calendar = FakeCalendar()
    policy = AvailabilityPolicy(
        publication_lag_sessions=1,
        max_observation_lag_sessions=2,
        publication_time_known=False,
    )

    with pytest.raises(MarketDataAvailabilityError, match="maximum observation lag"):
        align_auxiliary(
            [SignalDecisionTime.for_primary_session(date(2026, 8, 6))],
            frame(["2026-08-03"], [10.0]),
            policy=policy,
            calendar=calendar,
        )


def test_auxiliary_alignment_can_mark_excess_lag_decision_unavailable() -> None:
    calendar = FakeCalendar()
    policy = GapAwareAvailabilityPolicy(
        publication_lag_sessions=1,
        max_observation_lag_sessions=2,
        publication_time_known=False,
    )

    aligned = align_auxiliary(
        [
            SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
            SignalDecisionTime.for_primary_session(date(2026, 8, 6)),
        ],
        frame(["2026-08-03"], [10.0]),
        policy=policy,
        calendar=calendar,
    )

    assert list(aligned["ObservationAvailable"]) == [True, False]
    assert list(aligned["ObservationLagSessions"]) == [1, 3]
    assert list(aligned["Close"]) == [10.0, 10.0]


def test_market_data_bundle_is_complete_and_read_only() -> None:
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
    source = frame(["2026-08-03"], [10.0])
    bundle = MarketDataBundle.from_requirements(
        requirements,
        {primary: source, auxiliary: source},
        decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )

    returned = bundle[primary]
    returned.loc[:, "Close"] = 999

    assert bundle[primary].iloc[0]["Close"] == 10.0
    with pytest.raises(TypeError):
        bundle.series[primary] = source


def test_market_data_bundle_rejects_missing_declared_series() -> None:
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    requirement = MarketDataRequirement(primary, date(2020, 1, 1), role="primary")

    with pytest.raises(MarketDataAvailabilityError, match="missing declared series"):
        MarketDataBundle.from_requirements(
            (requirement,),
            {},
            decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 3)),
        )


def test_market_data_bundle_enforces_declared_history_coverage() -> None:
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    requirement = MarketDataRequirement(primary, date(2026, 7, 31), role="primary")

    with pytest.raises(MarketDataAvailabilityError, match="history starts at 2026-08-03"):
        MarketDataBundle.from_requirements(
            (requirement,),
            {primary: frame(["2026-08-03"], [10.0])},
            decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 3)),
        )


def test_market_data_bundle_rejects_duplicate_series_declarations() -> None:
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    requirement = MarketDataRequirement(primary, date(2026, 8, 3), role="primary")

    with pytest.raises(MarketDataAvailabilityError, match="declared more than once"):
        MarketDataBundle.from_requirements(
            (requirement, requirement),
            {primary: frame(["2026-08-03"], [10.0])},
            decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 3)),
        )


def test_market_data_bundle_rejects_missing_primary_session() -> None:
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    requirement = MarketDataRequirement(primary, date(2026, 8, 3), role="primary")

    with pytest.raises(MarketDataAvailabilityError, match="missing expected primary sessions"):
        MarketDataBundle.from_requirements(
            (requirement,),
            {primary: frame(["2026-08-03", "2026-08-05"], [10.0, 12.0])},
            decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 5)),
        )


def test_market_data_bundle_constructor_cannot_bypass_declarations() -> None:
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")

    with pytest.raises(MarketDataAvailabilityError, match="requires declarations"):
        MarketDataBundle(
            (),
            {primary: frame(["2026-08-03"], [10.0])},
            decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 3)),
        )


def test_bundle_auxiliary_access_enforces_declared_availability_policy() -> None:
    calendar = FakeCalendar()
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

    bundle = MarketDataBundle.from_requirements(
        requirements,
        {
            primary: frame(["2026-08-03", "2026-08-04"], [100.0, 101.0]),
            auxiliary: frame(["2026-08-03", "2026-08-04"], [10.0, 20.0]),
        },
        decision_time=SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        calendar=calendar,
    )

    available = bundle[auxiliary]

    assert list(available["ObservationDate"].dt.strftime("%Y-%m-%d")) == ["2026-08-03"]
    assert list(available["Close"]) == [10.0]
