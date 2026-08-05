"""Read-only declared bundles and backward as-of auxiliary alignment."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from types import MappingProxyType

import pandas as pd

from trading.market_data.calendar import PrimaryUSSessionCalendar
from trading.market_data.contracts import SessionCalendar
from trading.market_data.models import (
    AvailabilityPolicy,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
)
from trading.market_data.validation import validate_daily_bars


class MarketDataAvailabilityError(RuntimeError):
    """A declared series cannot safely satisfy a signal decision."""


class MarketDataBundle(Mapping[MarketDataSeries, pd.DataFrame]):
    """Complete defensive-copy view of the data declared for one execution."""

    def __init__(
        self,
        requirements: Iterable[MarketDataRequirement],
        frames: Mapping[MarketDataSeries, pd.DataFrame],
        *,
        decision_time: SignalDecisionTime,
        calendar: SessionCalendar | None = None,
    ) -> None:
        requirement_list = self.validate_requirements(requirements)
        session_calendar = calendar or PrimaryUSSessionCalendar()
        validated = self._validate_frames(requirement_list, frames, session_calendar)
        requirement_by_series = {
            requirement.series: requirement for requirement in requirement_list
        }
        accessible: dict[MarketDataSeries, pd.DataFrame] = {}
        for series, normalized in validated.items():
            requirement = requirement_by_series[series]
            if requirement.role == "auxiliary":
                policy = requirement.availability_policy
                if policy is None:  # pragma: no cover - guarded by the value type
                    raise MarketDataAvailabilityError(
                        f"auxiliary series {series.symbol} has no availability policy"
                    )
                accessible[series] = align_auxiliary(
                    (decision_time,),
                    normalized,
                    policy=policy,
                    calendar=session_calendar,
                )
            else:
                accessible[series] = normalized.loc[: pd.Timestamp(decision_time.session)]
        self._frames = accessible

    @staticmethod
    def validate_requirements(
        requirements: Iterable[MarketDataRequirement],
    ) -> tuple[MarketDataRequirement, ...]:
        requirement_list = tuple(requirements)
        if not requirement_list:
            raise MarketDataAvailabilityError("a market-data bundle requires declarations")
        required = {requirement.series for requirement in requirement_list}
        if len(required) != len(requirement_list):
            raise MarketDataAvailabilityError("a market-data series was declared more than once")
        return requirement_list

    @classmethod
    def from_requirements(
        cls,
        requirements: Iterable[MarketDataRequirement],
        frames: Mapping[MarketDataSeries, pd.DataFrame],
        *,
        decision_time: SignalDecisionTime,
        calendar: SessionCalendar | None = None,
    ) -> MarketDataBundle:
        return cls(
            requirements,
            frames,
            decision_time=decision_time,
            calendar=calendar,
        )

    @classmethod
    def _validate_frames(
        cls,
        requirements: Iterable[MarketDataRequirement],
        frames: Mapping[MarketDataSeries, pd.DataFrame],
        calendar: SessionCalendar,
    ) -> dict[MarketDataSeries, pd.DataFrame]:
        requirement_list = cls.validate_requirements(requirements)
        required = {requirement.series for requirement in requirement_list}
        missing = required.difference(frames)
        if missing:
            symbols = ", ".join(sorted(item.symbol for item in missing))
            raise MarketDataAvailabilityError(f"missing declared series: {symbols}")
        undeclared = set(frames).difference(required)
        if undeclared:
            symbols = ", ".join(sorted(item.symbol for item in undeclared))
            raise MarketDataAvailabilityError(f"bundle contains undeclared series: {symbols}")
        requirement_by_series = {
            requirement.series: requirement for requirement in requirement_list
        }
        validated: dict[MarketDataSeries, pd.DataFrame] = {}
        for series in required:
            normalized, outcome = validate_daily_bars(frames[series])
            if outcome.is_valid and not normalized.empty:
                expected_sessions = calendar.sessions_in_range(
                    normalized.index[0].date(),
                    normalized.index[-1].date(),
                )
                normalized, outcome = validate_daily_bars(
                    normalized,
                    expected_sessions=expected_sessions,
                )
            if not outcome.is_valid:
                raise MarketDataAvailabilityError(
                    f"invalid declared series {series.symbol}: {'; '.join(outcome.errors)}"
                )
            requirement = requirement_by_series[series]
            first_required_session = calendar.session_on_or_after(requirement.history_start)
            first_observation = normalized.index[0].date()
            if first_observation > first_required_session:
                raise MarketDataAvailabilityError(
                    f"{series.symbol} history starts at "
                    f"{first_observation}, after required session {first_required_session}"
                )
            validated[series] = normalized
        return validated

    @property
    def series(self) -> Mapping[MarketDataSeries, pd.DataFrame]:
        return MappingProxyType(
            {series: frame.copy(deep=True) for series, frame in self._frames.items()}
        )

    def __getitem__(self, key: MarketDataSeries) -> pd.DataFrame:
        return self._frames[key].copy(deep=True)

    def __iter__(self) -> Iterator[MarketDataSeries]:
        return iter(self._frames)

    def __len__(self) -> int:
        return len(self._frames)


def align_auxiliary(
    decisions: Iterable[SignalDecisionTime],
    auxiliary: pd.DataFrame,
    *,
    policy: AvailabilityPolicy,
    calendar: SessionCalendar,
) -> pd.DataFrame:
    """Align observations backward by declared information availability only."""
    normalized, outcome = validate_daily_bars(auxiliary)
    if not outcome.is_valid:
        raise MarketDataAvailabilityError("invalid auxiliary series: " + "; ".join(outcome.errors))
    observations: list[dict[str, object]] = []
    for observation_date, row in normalized.iterrows():
        anchor = calendar.session_on_or_after(observation_date.date())
        available = calendar.session_offset(anchor, policy.publication_lag_sessions)
        observations.append(
            {
                "observation_date": observation_date,
                "available_session": pd.Timestamp(available),
                "row": row,
            }
        )

    aligned_rows: list[dict[str, object]] = []
    decision_index: list[pd.Timestamp] = []
    for decision in decisions:
        eligible = [
            observation
            for observation in observations
            if observation["available_session"] <= pd.Timestamp(decision.session)
        ]
        if not eligible:
            raise MarketDataAvailabilityError(
                f"no auxiliary observation available by signal decision {decision.session}"
            )
        selected = eligible[-1]
        observation_date = selected["observation_date"]
        lag = calendar.session_distance(observation_date.date(), decision.session)
        if lag > policy.max_observation_lag_sessions:
            raise MarketDataAvailabilityError(
                f"maximum observation lag exceeded at signal decision {decision.session}: {lag}"
            )
        row = selected["row"].to_dict()
        row.update(
            ObservationDate=observation_date,
            AvailableSession=selected["available_session"],
            ObservationLagSessions=lag,
        )
        aligned_rows.append(row)
        decision_index.append(pd.Timestamp(decision.session))

    result = pd.DataFrame(
        aligned_rows, index=pd.DatetimeIndex(decision_index, name="DecisionSession")
    )
    return result
