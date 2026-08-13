"""Workflow-native XLF pullbacks with close-armed profit protection."""

from __future__ import annotations

import math
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
class ProfitProtectionPullbackTrialConfig:
    """Frozen entry, state-machine, occupation-lock, and exit semantics."""

    ticker: str
    history_start: date
    research_start: date
    holding_sessions: int
    entry_lag_sessions: int
    pullback_lookback: int
    pullback_threshold: float
    bollinger_lookback: int
    bollinger_stddevs: float
    arm_return: float | None = None
    floor_return: float | None = None
    protection_exit_lag_sessions: int = 1

    def __post_init__(self) -> None:
        if self.holding_sessions <= 0:
            raise ValueError("holding_sessions must be positive")
        if self.entry_lag_sessions <= 0:
            raise ValueError("entry_lag_sessions must be positive")
        if self.pullback_lookback <= 0 or self.bollinger_lookback < 2:
            raise ValueError("indicator lookbacks are invalid")
        if self.pullback_threshold >= 0:
            raise ValueError("pullback_threshold must be negative")
        if self.bollinger_stddevs <= 0:
            raise ValueError("bollinger_stddevs must be positive")
        if self.protection_exit_lag_sessions <= 0:
            raise ValueError("protection_exit_lag_sessions must be positive")
        if self.arm_return is None:
            if self.floor_return is not None or self.protection_exit_lag_sessions != 1:
                raise ValueError("fixed baseline must not declare profit-protection behavior")
            return
        if self.floor_return is None:
            raise ValueError("armed trials require a floor_return")
        if self.floor_return < 0 or self.floor_return >= self.arm_return:
            raise ValueError("floor_return must be non-negative and below arm_return")


@dataclass(frozen=True, slots=True)
class ProfitProtectionBuildResult:
    """Gross candidates plus raw and occupation-locked signal diagnostics."""

    candidates: tuple[CandidateTrade, ...]
    raw_signals: tuple[date, ...]
    occupation_lock_skips: tuple[date, ...]


@dataclass(frozen=True, slots=True)
class ProfitProtectionPullbackResearchDefinition:
    """Permanent primary-only XLF pullback definition with a fixed exit state machine."""

    identity: str
    result_name: str
    family: str
    hypothesis: str
    config: ProfitProtectionPullbackTrialConfig
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
        primary = bundle[requirement.series]
        research = primary.loc[pd.Timestamp(self.config.research_start) :]
        built = build_profit_protection_candidates(primary, self.config)
        return {
            "metadata": {
                "research_definition": self.identity,
                "ticker": self.config.ticker,
                "auxiliary_ticker": None,
                "data_cutoff": primary.index[-1].date().isoformat(),
                "accepted_entry_dates": tuple(
                    candidate.entry_date.isoformat() for candidate in built.candidates
                ),
                "occupation_lock_skips": tuple(
                    signal.isoformat() for signal in built.occupation_lock_skips
                ),
            },
            "canonical_sleeve_input": CanonicalSleeveInput(
                calendar=tuple(research.index),
                close_prices=research["Close"].copy(deep=True),
                candidates=built.candidates,
                raw_signals=built.raw_signals,
                legacy_signals=built.raw_signals,
                legacy_candidates=built.candidates,
                initial_capital=1.0,
            ),
        }


def build_profit_protection_candidates(
    primary: pd.DataFrame,
    config: ProfitProtectionPullbackTrialConfig,
) -> ProfitProtectionBuildResult:
    """Build one entry cohort under the frozen ten-session occupation lock."""
    _validate_primary_frame(primary)
    close = primary["Close"]
    rolling = close.rolling(config.bollinger_lookback)
    lower_band = rolling.mean() - config.bollinger_stddevs * rolling.std(ddof=1)
    eligible = close.le(lower_band) & close.pct_change(config.pullback_lookback).le(
        config.pullback_threshold
    )
    final_dependency = config.entry_lag_sessions + config.holding_sessions
    raw_positions = tuple(
        position
        for position, active in enumerate(eligible.fillna(False).to_numpy())
        if active
        and primary.index[position].date() >= config.research_start
        and position + final_dependency < len(primary)
    )

    candidates: list[CandidateTrade] = []
    skipped_positions: list[int] = []
    occupation_until_position = -1
    for signal_position in raw_positions:
        entry_position = signal_position + config.entry_lag_sessions
        if entry_position < occupation_until_position:
            skipped_positions.append(signal_position)
            continue
        candidates.append(build_profit_protection_candidate(primary, signal_position, config))
        occupation_until_position = entry_position + config.holding_sessions

    return ProfitProtectionBuildResult(
        candidates=tuple(candidates),
        raw_signals=tuple(primary.index[position].date() for position in raw_positions),
        occupation_lock_skips=tuple(
            primary.index[position].date() for position in skipped_positions
        ),
    )


def build_profit_protection_candidate(
    primary: pd.DataFrame,
    signal_position: int,
    config: ProfitProtectionPullbackTrialConfig,
) -> CandidateTrade:
    """Build one gross next-open candidate from a known eligible signal position."""
    _validate_primary_frame(primary)
    entry_position = signal_position + config.entry_lag_sessions
    expiry_position = entry_position + config.holding_sessions
    if signal_position < 0 or expiry_position >= len(primary):
        raise ValueError("signal position lacks the frozen entry and exit horizon")

    entry_price = _finite_open(primary, entry_position, "entry")
    exit_position = expiry_position
    exit_type = "time_expiry"
    arm_position: int | None = None

    if config.arm_return is not None:
        floor_return = config.floor_return
        if floor_return is None:  # pragma: no cover - config validation prevents this
            raise ValueError("armed trial is missing floor_return")
        arm_price = entry_price * (1.0 + config.arm_return)
        floor_price = entry_price * (1.0 + floor_return)
        for decision_position in range(entry_position, expiry_position):
            decision_close = _finite_close(primary, decision_position)
            if arm_position is None:
                if decision_close >= arm_price:
                    arm_position = decision_position
                continue
            if decision_close <= floor_price:
                scheduled_exit = decision_position + config.protection_exit_lag_sessions
                if scheduled_exit < expiry_position:
                    exit_position = scheduled_exit
                    exit_type = "profit_protection"
                break

    return CandidateTrade(
        signal_date=primary.index[signal_position].date(),
        entry_date=primary.index[entry_position].date(),
        entry_price=entry_price,
        exit_date=primary.index[exit_position].date(),
        exit_price=_finite_open(primary, exit_position, "exit"),
        exit_type=exit_type,
    )


def _validate_primary_frame(primary: pd.DataFrame) -> None:
    if not {"Open", "Close"}.issubset(primary.columns):
        raise ValueError("primary data requires Open and Close columns")
    if primary.empty or not primary.index.is_monotonic_increasing or not primary.index.is_unique:
        raise ValueError("primary data index must be non-empty, unique, and increasing")


def _finite_open(primary: pd.DataFrame, position: int, role: str) -> float:
    value = float(primary.iloc[position]["Open"])
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{role} open must be finite and positive")
    return value


def _finite_close(primary: pd.DataFrame, position: int) -> float:
    value = float(primary.iloc[position]["Close"])
    if not math.isfinite(value) or value <= 0:
        raise ValueError("decision close must be finite and positive")
    return value
