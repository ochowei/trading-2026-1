"""Read-only declared bundles and backward as-of auxiliary alignment."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from types import MappingProxyType

import pandas as pd

from trading.market_data.calendar import PrimaryUSSessionCalendar
from trading.market_data.contracts import SessionCalendar
from trading.market_data.models import (
    AvailabilityPolicy,
    MarketDataDeclaration,
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
        requirements: Iterable[MarketDataRequirement] | MarketDataDeclaration,
        frames: Mapping[MarketDataSeries, pd.DataFrame],
        *,
        decision_time: SignalDecisionTime,
        decision_times: Iterable[SignalDecisionTime] | None = None,
        calendar: SessionCalendar | None = None,
    ) -> None:
        declaration = self._declaration_from(requirements)
        requirement_list = declaration.requirements
        session_calendar = calendar or PrimaryUSSessionCalendar()
        decision_time_list = self._validate_decision_times(
            decision_time,
            decision_times,
        )
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
                    decision_time_list,
                    normalized,
                    policy=policy,
                    calendar=session_calendar,
                )
            else:
                accessible[series] = normalized.loc[: pd.Timestamp(decision_time.session)]
        self._declaration = declaration
        self._decision_times = decision_time_list
        self._decision_time = decision_time
        self._frames = accessible

    @staticmethod
    def validate_requirements(
        requirements: Iterable[MarketDataRequirement] | MarketDataDeclaration,
    ) -> tuple[MarketDataRequirement, ...]:
        return MarketDataBundle._declaration_from(requirements).requirements

    @staticmethod
    def _declaration_from(
        requirements: Iterable[MarketDataRequirement] | MarketDataDeclaration,
    ) -> MarketDataDeclaration:
        if isinstance(requirements, MarketDataDeclaration):
            return requirements
        try:
            return MarketDataDeclaration.from_requirements(requirements)
        except ValueError as exc:
            raise MarketDataAvailabilityError(str(exc)) from exc

    @staticmethod
    def _validate_decision_times(
        decision_time: SignalDecisionTime,
        decision_times: Iterable[SignalDecisionTime] | None,
    ) -> tuple[SignalDecisionTime, ...]:
        values = tuple(decision_times) if decision_times is not None else (decision_time,)
        if not values:
            raise MarketDataAvailabilityError("a bundle requires decision sessions")
        if any(not isinstance(item, SignalDecisionTime) for item in values):
            raise MarketDataAvailabilityError("decision sessions must be SignalDecisionTime values")
        sessions = tuple(item.session for item in values)
        if len(set(sessions)) != len(sessions):
            raise MarketDataAvailabilityError("decision sessions must be unique and chronological")
        if sessions != tuple(sorted(sessions)):
            raise MarketDataAvailabilityError("decision sessions must be chronological")
        if values[-1].session != decision_time.session:
            raise MarketDataAvailabilityError("the final decision session must match decision_time")
        return values

    @classmethod
    def from_requirements(
        cls,
        requirements: Iterable[MarketDataRequirement],
        frames: Mapping[MarketDataSeries, pd.DataFrame],
        *,
        decision_time: SignalDecisionTime,
        decision_times: Iterable[SignalDecisionTime] | None = None,
        calendar: SessionCalendar | None = None,
    ) -> MarketDataBundle:
        return cls(
            requirements,
            frames,
            decision_time=decision_time,
            decision_times=decision_times,
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
        validated: dict[MarketDataSeries, pd.DataFrame] = {}
        # Keep declaration order stable.  The execution contract treats the
        # primary series as the first item and auxiliary series as the
        # subsequent declared inputs; iterating a set here made bundle
        # iteration nondeterministic and broke that contract for multi-series
        # strategies.
        for requirement in requirement_list:
            series = requirement.series
            normalized, outcome = validate_daily_bars(frames[series])
            if (
                outcome.is_valid
                and not normalized.empty
                and requirement.coverage_policy.requires_complete_sessions
            ):
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

    @property
    def declaration(self) -> MarketDataDeclaration:
        return self._declaration

    @property
    def requirements(self) -> tuple[MarketDataRequirement, ...]:
        return self._declaration.requirements

    @property
    def decision_time(self) -> SignalDecisionTime:
        return self._decision_time

    @property
    def decision_times(self) -> tuple[SignalDecisionTime, ...]:
        return self._decision_times

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
    decision_list = tuple(decisions)
    if not decision_list:
        raise MarketDataAvailabilityError("auxiliary alignment requires decision sessions")
    normalized, outcome = validate_daily_bars(auxiliary)
    if not outcome.is_valid:
        raise MarketDataAvailabilityError("invalid auxiliary series: " + "; ".join(outcome.errors))
    latest_decision = max(decision.session for decision in decision_list)
    observations: list[dict[str, object]] = []
    for observation_date, row in normalized.iterrows():
        if observation_date.date() > latest_decision:
            continue
        anchor = calendar.session_on_or_after(observation_date.date())
        try:
            available = calendar.session_offset(anchor, policy.publication_lag_sessions)
        except (IndexError, KeyError, ValueError):
            continue
        if available > latest_decision:
            continue
        observations.append(
            {
                "observation_date": observation_date,
                "available_session": pd.Timestamp(available),
                "row": row,
            }
        )

    aligned_rows: list[dict[str, object]] = []
    decision_index: list[pd.Timestamp] = []
    for decision in decision_list:
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
