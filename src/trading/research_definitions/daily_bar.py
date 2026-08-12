"""Reusable workflow-native daily-bar definition and execution seams."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from trading.core.sleeve_engine import (
    CANONICAL_SLEEVE_ENGINE_VERSION,
    CandidateTrade,
    CanonicalSleeveInput,
    ExecutionCostPolicy,
)
from trading.market_data import MarketDataBundle, MarketDataRequirement, MarketDataSeries
from trading.policies import PolicySet
from trading.research_data import (
    ExperimentTrialDeclaration,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
)


@dataclass(frozen=True, slots=True)
class DailyBarTrialConfig:
    """Frozen semantic inputs for a simple primary-only pilot trial."""

    ticker: str
    history_start: date
    research_start: date
    signal_kind: str
    holding_sessions: int
    consecutive_down_sessions: int | None = None

    def __post_init__(self) -> None:
        if self.signal_kind not in {"down-streak", "periodic-baseline"}:
            raise ValueError("unsupported daily-bar signal kind")
        if self.holding_sessions <= 0:
            raise ValueError("holding_sessions must be positive")
        if self.signal_kind == "down-streak" and (
            self.consecutive_down_sessions is None or self.consecutive_down_sessions < 2
        ):
            raise ValueError("down-streak trials require at least two down sessions")
        if self.signal_kind == "periodic-baseline" and self.consecutive_down_sessions is not None:
            raise ValueError("periodic baseline must not declare a down-streak threshold")


@dataclass(frozen=True, slots=True)
class DailyBarResearchDefinition:
    """A permanent workflow-native trial backed by one declarative source file."""

    identity: str
    result_name: str
    family: str
    hypothesis: str
    config: DailyBarTrialConfig
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
        candidates, signals = build_candidates(frame, self.config)
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


def build_candidates(
    frame: pd.DataFrame,
    config: DailyBarTrialConfig,
) -> tuple[tuple[CandidateTrade, ...], tuple[date, ...]]:
    """Build gross next-open entries and fixed next-open expiry exits."""
    if config.signal_kind == "down-streak":
        down = frame["Close"].diff().lt(0)
        threshold = config.consecutive_down_sessions
        if threshold is None:  # pragma: no cover - config validation prevents this
            raise ValueError("down-streak threshold is missing")
        eligible = down.rolling(threshold).sum().eq(threshold).to_numpy()
    else:
        eligible = pd.Series(True, index=frame.index).to_numpy()
    positions = [
        position
        for position, active in enumerate(eligible)
        if active
        and frame.index[position].date() >= config.research_start
        and position + config.holding_sessions + 1 < len(frame)
    ]
    candidates = tuple(
        CandidateTrade(
            signal_date=frame.index[position].date(),
            entry_date=frame.index[position + 1].date(),
            entry_price=float(frame.iloc[position + 1]["Open"]),
            exit_date=frame.index[position + config.holding_sessions + 1].date(),
            exit_price=float(frame.iloc[position + config.holding_sessions + 1]["Open"]),
            exit_type="time_expiry",
        )
        for position in positions
    )
    return candidates, tuple(frame.index[position].date() for position in positions)


def execution_cost_policies(
    policy_set: PolicySet,
) -> tuple[ExecutionCostPolicy, ExecutionCostPolicy]:
    """Resolve the exact canonical base/stress values selected by the workflow."""
    try:
        release = next(
            item for item in policy_set.releases if item.identity.family == "canonical-execution"
        )
        base = release.values["base_cost_bps"]
        stress = release.values["stress_cost_bps"]
        return (
            ExecutionCostPolicy(
                entry_slippage_bps=float(base["entry_slippage"]),
                exit_slippage_bps=float(base["exit_slippage"]),
                fee_bps_per_side=float(base["fee_per_side"]),
            ),
            ExecutionCostPolicy(
                entry_slippage_bps=float(stress["entry_slippage"]),
                exit_slippage_bps=float(stress["exit_slippage"]),
                fee_bps_per_side=float(stress["fee_per_side"]),
            ),
        )
    except (KeyError, StopIteration, TypeError, ValueError) as exc:
        raise ValueError("policy set lacks canonical execution cost values") from exc
