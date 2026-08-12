"""Workflow-native monthly-calendar daily-bar research definitions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from trading.core.sleeve_engine import (
    CANONICAL_SLEEVE_ENGINE_VERSION,
    CandidateTrade,
    CanonicalSleeveInput,
)
from trading.market_data import MarketDataBundle, MarketDataRequirement, MarketDataSeries
from trading.policies import PolicySet
from trading.research_data import (
    ExperimentTrialDeclaration,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
)
from trading.research_definitions.daily_bar import execution_cost_policies


@dataclass(frozen=True, slots=True)
class MonthlyCalendarTrialConfig:
    """Frozen semantics for one monthly entry session and fixed holding period."""

    ticker: str
    history_start: date
    research_start: date
    holding_sessions: int
    entry_kind: str
    month_end_offset: int | None = None
    session_ordinal: int | None = None

    def __post_init__(self) -> None:
        if self.holding_sessions <= 0:
            raise ValueError("holding_sessions must be positive")
        if self.entry_kind == "month-end-offset":
            if self.month_end_offset not in {-2, -1, 0} or self.session_ordinal is not None:
                raise ValueError("month-end entry requires one supported offset")
        elif self.entry_kind == "session-ordinal":
            if self.session_ordinal != 10 or self.month_end_offset is not None:
                raise ValueError("baseline entry requires the tenth monthly session")
        else:
            raise ValueError("unsupported monthly-calendar entry kind")


@dataclass(frozen=True, slots=True)
class MonthlyCalendarResearchDefinition:
    """Permanent policy-bound source identity for one monthly-calendar trial."""

    identity: str
    result_name: str
    family: str
    hypothesis: str
    config: MonthlyCalendarTrialConfig
    source_path: Path

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        return (
            MarketDataRequirement(
                MarketDataSeries.yahoo_adjusted_daily(self.config.ticker),
                self.config.history_start,
                role="primary",
            ),
        )

    def declare_experiment_trial(self) -> ExperimentTrialDeclaration:
        return ExperimentTrialDeclaration(family=self.family, hypothesis=self.hypothesis)

    def capture_research_definition(
        self,
        store: ResearchDefinitionStore,
        policy_set: PolicySet,
    ) -> ResearchDefinitionSnapshot:
        base, stress = execution_cost_policies(policy_set)
        runtime_path = Path(__file__).resolve()
        return store.capture(
            resolved_config={
                "identity": self.identity,
                "config": asdict(self.config),
                "market_data_requirements": self.market_data_requirements(),
            },
            sources={
                "strategy": self.source_path.resolve(),
                "detector": runtime_path,
                "backtester": runtime_path,
            },
            execution_engine_version=CANONICAL_SLEEVE_ENGINE_VERSION,
            dependency_versions={"pandas": pd.__version__},
            base_cost_policy=base,
            stress_cost_policy=stress,
            policy_set=policy_set,
            workflow_native=True,
        )

    def run_with_bundle(self, bundle: MarketDataBundle) -> dict[str, object]:
        requirement = self.market_data_requirements()[0]
        if tuple(bundle) != (requirement.series,):
            raise ValueError("bundle keys do not match the frozen primary-series declaration")
        frame = bundle[requirement.series]
        research = frame.loc[pd.Timestamp(self.config.research_start) :]
        candidates, signals = build_monthly_candidates(frame, self.config)
        return {
            "metadata": {
                "research_definition": self.identity,
                "ticker": self.config.ticker,
                "data_cutoff": frame.index[-1].date().isoformat(),
            },
            "canonical_sleeve_input": CanonicalSleeveInput(
                calendar=tuple(research.index),
                close_prices=research["Close"].copy(deep=True),
                candidates=candidates,
                raw_signals=signals,
                legacy_signals=signals,
                legacy_candidates=candidates,
                initial_capital=1.0,
            ),
        }


def build_monthly_candidates(
    frame: pd.DataFrame,
    config: MonthlyCalendarTrialConfig,
) -> tuple[tuple[CandidateTrade, ...], tuple[date, ...]]:
    """Build one monthly next-open entry and fixed next-open expiry when complete."""
    positions = pd.Series(range(len(frame)), index=frame.index)
    selected: list[int] = []
    for _, monthly in positions.groupby(frame.index.to_period("M")):
        if config.entry_kind == "month-end-offset":
            offset = config.month_end_offset
            if offset is None:  # pragma: no cover - config validation prevents this
                raise ValueError("month-end offset is missing")
            required_sessions = abs(offset) + 1
            if len(monthly) < required_sessions:
                continue
            entry_position = int(monthly.iloc[offset - 1])
        else:
            ordinal = config.session_ordinal
            if ordinal is None:  # pragma: no cover - config validation prevents this
                raise ValueError("session ordinal is missing")
            if len(monthly) < ordinal:
                continue
            entry_position = int(monthly.iloc[ordinal - 1])
        exit_position = entry_position + config.holding_sessions
        if (
            entry_position > 0
            and frame.index[entry_position].date() >= config.research_start
            and exit_position < len(frame)
        ):
            selected.append(entry_position)
    candidates = tuple(
        CandidateTrade(
            signal_date=frame.index[position - 1].date(),
            entry_date=frame.index[position].date(),
            entry_price=float(frame.iloc[position]["Open"]),
            exit_date=frame.index[position + config.holding_sessions].date(),
            exit_price=float(frame.iloc[position + config.holding_sessions]["Open"]),
            exit_type="time_expiry",
        )
        for position in selected
    )
    return candidates, tuple(frame.index[position - 1].date() for position in selected)
