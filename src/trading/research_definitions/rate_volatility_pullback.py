"""Workflow-native rate-volatility-conditioned pullback definitions."""

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
from trading.market_data import (
    AvailabilityPolicy,
    MarketDataBundle,
    MarketDataCoveragePolicy,
    MarketDataRequirement,
    MarketDataSeries,
)
from trading.policies import PolicySet
from trading.research_data import (
    ExperimentTrialDeclaration,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
)
from trading.research_definitions.daily_bar import execution_cost_policies


@dataclass(frozen=True, slots=True)
class RateVolatilityPullbackTrialConfig:
    """Frozen semantics for one pullback candidate or its ungated baseline."""

    ticker: str
    history_start: date
    research_start: date
    holding_sessions: int
    entry_lag_sessions: int
    pullback_lookback: int
    pullback_threshold: float
    bollinger_lookback: int
    bollinger_stddevs: float
    move_ticker: str | None = None
    move_change_sessions: int | None = None
    move_change_cap: float | None = None
    auxiliary_max_lag_sessions: int = 3

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
        move_fields = (
            self.move_ticker is not None,
            self.move_change_sessions is not None,
            self.move_change_cap is not None,
        )
        if any(move_fields) and not all(move_fields):
            raise ValueError("MOVE gate fields must be declared together")
        if self.move_change_sessions is not None and self.move_change_sessions <= 0:
            raise ValueError("move_change_sessions must be positive")
        if self.auxiliary_max_lag_sessions < 1:
            raise ValueError("auxiliary_max_lag_sessions must be positive")


@dataclass(frozen=True, slots=True)
class RateVolatilityPullbackResearchDefinition:
    """Permanent policy-bound source identity for an XLF pullback trial."""

    identity: str
    result_name: str
    family: str
    hypothesis: str
    config: RateVolatilityPullbackTrialConfig
    source_path: Path

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        primary = MarketDataRequirement(
            MarketDataSeries.yahoo_adjusted_daily(self.config.ticker),
            self.config.history_start,
            role="primary",
        )
        if self.config.move_ticker is None:
            return (primary,)
        return (
            primary,
            MarketDataRequirement(
                MarketDataSeries.yahoo_adjusted_daily(self.config.move_ticker),
                self.config.history_start,
                role="auxiliary",
                availability_policy=AvailabilityPolicy(
                    publication_lag_sessions=1,
                    max_observation_lag_sessions=self.config.auxiliary_max_lag_sessions,
                    publication_time_known=False,
                ),
                coverage_policy=MarketDataCoveragePolicy.provider_observations(),
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
        requirements = self.market_data_requirements()
        if tuple(bundle) != tuple(item.series for item in requirements):
            raise ValueError("bundle keys do not match the frozen data declaration")
        primary = bundle[requirements[0].series]
        auxiliary = bundle[requirements[1].series] if len(requirements) == 2 else None
        research = primary.loc[pd.Timestamp(self.config.research_start) :]
        candidates, signals = build_rate_volatility_candidates(
            primary,
            auxiliary,
            self.config,
        )
        return {
            "metadata": {
                "research_definition": self.identity,
                "ticker": self.config.ticker,
                "auxiliary_ticker": self.config.move_ticker,
                "data_cutoff": primary.index[-1].date().isoformat(),
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


def build_rate_volatility_candidates(
    primary: pd.DataFrame,
    auxiliary: pd.DataFrame | None,
    config: RateVolatilityPullbackTrialConfig,
) -> tuple[tuple[CandidateTrade, ...], tuple[date, ...]]:
    """Build next-open pullback entries with an optional backward-as-of MOVE gate."""
    close = primary["Close"]
    rolling = close.rolling(config.bollinger_lookback)
    lower_band = rolling.mean() - config.bollinger_stddevs * rolling.std(ddof=1)
    eligible = close.le(lower_band) & close.pct_change(config.pullback_lookback).le(
        config.pullback_threshold
    )
    if config.move_change_cap is not None:
        if auxiliary is None:
            raise ValueError("gated trial requires aligned MOVE observations")
        required_columns = {"Close", "ObservationDate", "ObservationLagSessions"}
        if not required_columns.issubset(auxiliary.columns):
            raise ValueError("aligned MOVE observations lack availability evidence")
        if not primary.index.isin(auxiliary.index).all():
            raise ValueError("aligned MOVE observations do not cover every primary session")
        if (auxiliary["ObservationLagSessions"] < 1).any():
            raise ValueError("MOVE observations must be backward-as-of")
        move_change_sessions = config.move_change_sessions
        if move_change_sessions is None:  # pragma: no cover - config validation prevents this
            raise ValueError("MOVE change window is missing")
        move_change = auxiliary["Close"].reindex(primary.index).diff(move_change_sessions)
        eligible &= move_change.le(config.move_change_cap)

    final_dependency = config.entry_lag_sessions + config.holding_sessions
    positions = [
        position
        for position, active in enumerate(eligible.fillna(False).to_numpy())
        if active
        and primary.index[position].date() >= config.research_start
        and position + final_dependency < len(primary)
    ]
    candidates = tuple(
        CandidateTrade(
            signal_date=primary.index[position].date(),
            entry_date=primary.index[position + config.entry_lag_sessions].date(),
            entry_price=float(primary.iloc[position + config.entry_lag_sessions]["Open"]),
            exit_date=primary.index[position + final_dependency].date(),
            exit_price=float(primary.iloc[position + final_dependency]["Open"]),
            exit_type="time_expiry",
        )
        for position in positions
    )
    return candidates, tuple(primary.index[position].date() for position in positions)
