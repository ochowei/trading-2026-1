"""Workflow-native FXI ATR/divergence mean-reversion definitions."""

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
from trading.market_data import (
    AvailabilityPolicy,
    MarketDataBundle,
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
class FXIMeanReversionTrialConfig:
    """Frozen semantics for the FXI candidate, baseline, or robustness trial."""

    ticker: str
    history_start: date
    research_start: date
    holding_sessions: int
    entry_lag_sessions: int
    pullback_lookback: int
    pullback_threshold: float
    pullback_cap: float
    wr_period: int
    wr_threshold: float
    cooldown_sessions: int
    profit_target: float
    stop_loss: float
    close_position_threshold: float | None = None
    atr_short_period: int | None = None
    atr_long_period: int | None = None
    atr_ratio_floor: float | None = None
    atr_ratio_ceiling: float | None = None
    anchor_ticker: str | None = None
    relative_return_lookback: int | None = None
    relative_return_floor: float | None = None

    def __post_init__(self) -> None:
        if self.holding_sessions <= 0 or self.entry_lag_sessions <= 0:
            raise ValueError("holding and entry lag sessions must be positive")
        if self.pullback_lookback <= 1 or self.wr_period <= 1:
            raise ValueError("indicator lookbacks must exceed one session")
        if not self.pullback_cap < self.pullback_threshold < 0:
            raise ValueError("pullback cap must be deeper than the negative threshold")
        if not -100 <= self.wr_threshold <= 0:
            raise ValueError("Williams %R threshold must be between -100 and 0")
        if self.cooldown_sessions < 0:
            raise ValueError("cooldown_sessions must not be negative")
        if self.profit_target <= 0 or self.stop_loss >= 0:
            raise ValueError("target must be positive and stop must be negative")
        if self.close_position_threshold is not None and not (
            0 <= self.close_position_threshold <= 1
        ):
            raise ValueError("close-position threshold must be between zero and one")
        atr_fields = (
            self.atr_short_period,
            self.atr_long_period,
            self.atr_ratio_floor,
            self.atr_ratio_ceiling,
        )
        if any(item is not None for item in atr_fields) and not all(
            item is not None for item in atr_fields
        ):
            raise ValueError("ATR-band fields must be declared together")
        if self.atr_short_period is not None:
            if self.atr_short_period <= 0 or self.atr_long_period <= self.atr_short_period:
                raise ValueError("ATR periods must be positive and ordered")
            if self.atr_ratio_floor < 0 or self.atr_ratio_ceiling <= self.atr_ratio_floor:
                raise ValueError("ATR ratio band is invalid")
        relative_fields = (
            self.anchor_ticker,
            self.relative_return_lookback,
            self.relative_return_floor,
        )
        if any(item is not None for item in relative_fields) and not all(
            item is not None for item in relative_fields
        ):
            raise ValueError("relative-return fields must be declared together")
        if self.relative_return_lookback is not None and self.relative_return_lookback <= 0:
            raise ValueError("relative-return lookback must be positive")


@dataclass(frozen=True, slots=True)
class FXIMeanReversionResearchDefinition:
    """Permanent policy-bound source identity for one FXI mean-reversion trial."""

    identity: str
    result_name: str
    family: str
    hypothesis: str
    config: FXIMeanReversionTrialConfig
    source_path: Path

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        primary = MarketDataRequirement(
            MarketDataSeries.yahoo_adjusted_daily(self.config.ticker),
            self.config.history_start,
            role="primary",
        )
        if self.config.anchor_ticker is None:
            return (primary,)
        return (
            primary,
            MarketDataRequirement(
                MarketDataSeries.yahoo_adjusted_daily(self.config.anchor_ticker),
                self.config.history_start,
                role="auxiliary",
                availability_policy=AvailabilityPolicy(
                    publication_lag_sessions=0,
                    max_observation_lag_sessions=0,
                    publication_time_known=True,
                ),
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
        candidates, signals = build_fxi_mean_reversion_candidates(
            primary,
            auxiliary,
            self.config,
        )
        return {
            "metadata": {
                "research_definition": self.identity,
                "ticker": self.config.ticker,
                "auxiliary_ticker": self.config.anchor_ticker,
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


def build_fxi_mean_reversion_candidates(
    primary: pd.DataFrame,
    auxiliary: pd.DataFrame | None,
    config: FXIMeanReversionTrialConfig,
) -> tuple[tuple[CandidateTrade, ...], tuple[date, ...]]:
    """Build gross next-open FXI candidates with fixed target, stop, and expiry."""
    _require_price_columns(primary)
    indicators = compute_fxi_mean_reversion_indicators(primary, auxiliary, config)
    eligible = indicators["Pullback"].le(config.pullback_threshold)
    eligible &= indicators["Pullback"].ge(config.pullback_cap)
    eligible &= indicators["WR"].le(config.wr_threshold)
    if config.close_position_threshold is not None:
        eligible &= indicators["ClosePos"].ge(config.close_position_threshold)
    if config.atr_ratio_floor is not None:
        eligible &= indicators["ATR_Ratio"].gt(config.atr_ratio_floor)
        eligible &= indicators["ATR_Ratio"].le(config.atr_ratio_ceiling)
    if config.relative_return_floor is not None:
        eligible &= indicators["RelativeReturn"].ge(config.relative_return_floor)

    latest_signal_position: int | None = None
    signal_positions: list[int] = []
    final_dependency = config.entry_lag_sessions + config.holding_sessions + 1
    for position, active in enumerate(eligible.fillna(False).to_numpy()):
        if not active or primary.index[position].date() < config.research_start:
            continue
        if position + final_dependency >= len(primary):
            continue
        if (
            latest_signal_position is not None
            and position - latest_signal_position <= config.cooldown_sessions
        ):
            continue
        signal_positions.append(position)
        latest_signal_position = position

    candidates = tuple(
        build_fxi_mean_reversion_candidate(primary, position, config)
        for position in signal_positions
    )
    signals = tuple(primary.index[position].date() for position in signal_positions)
    return candidates, signals


def compute_fxi_mean_reversion_indicators(
    primary: pd.DataFrame,
    auxiliary: pd.DataFrame | None,
    config: FXIMeanReversionTrialConfig,
) -> pd.DataFrame:
    """Compute the exact preregistered primary and optional ASHR dimensions."""
    _require_price_columns(primary)
    result = pd.DataFrame(index=primary.index)
    rolling_high = primary["High"].rolling(config.pullback_lookback).max()
    result["Pullback"] = (primary["Close"] - rolling_high) / rolling_high

    wr_high = primary["High"].rolling(config.wr_period).max()
    wr_low = primary["Low"].rolling(config.wr_period).min()
    wr_range = wr_high - wr_low
    result["WR"] = (wr_high - primary["Close"]) / wr_range * -100
    result.loc[wr_range.eq(0), "WR"] = -50.0

    day_range = primary["High"] - primary["Low"]
    result["ClosePos"] = (primary["Close"] - primary["Low"]) / day_range
    result.loc[day_range.eq(0), "ClosePos"] = 0.5

    if config.atr_short_period is not None:
        true_range = pd.concat(
            (
                primary["High"] - primary["Low"],
                (primary["High"] - primary["Close"].shift(1)).abs(),
                (primary["Low"] - primary["Close"].shift(1)).abs(),
            ),
            axis=1,
        ).max(axis=1)
        atr_short = true_range.rolling(config.atr_short_period).mean()
        atr_long = true_range.rolling(config.atr_long_period).mean()
        result["ATR_Ratio"] = atr_short / atr_long

    if config.anchor_ticker is not None:
        if auxiliary is None:
            raise ValueError("ASHR-gated trial requires aligned auxiliary observations")
        required = {"Close", "ObservationDate", "ObservationLagSessions"}
        if not required.issubset(auxiliary.columns):
            raise ValueError("aligned ASHR observations lack availability evidence")
        if not primary.index.isin(auxiliary.index).all():
            raise ValueError("aligned ASHR observations do not cover every primary session")
        aligned = auxiliary.reindex(primary.index)
        if aligned["ObservationLagSessions"].ne(0).any():
            raise ValueError("ASHR observations must match the same completed session")
        observation_dates = pd.to_datetime(aligned["ObservationDate"])
        if not observation_dates.eq(primary.index.to_series(index=primary.index)).all():
            raise ValueError("ASHR observation dates must equal primary decision sessions")
        lookback = config.relative_return_lookback
        if lookback is None:  # pragma: no cover - config validation prevents this
            raise ValueError("relative-return lookback is missing")
        result["RelativeReturn"] = primary["Close"].pct_change(lookback) - aligned[
            "Close"
        ].pct_change(lookback)
    return result


def build_fxi_mean_reversion_candidate(
    primary: pd.DataFrame,
    signal_position: int,
    config: FXIMeanReversionTrialConfig,
) -> CandidateTrade:
    """Resolve one candidate using gross canonical target/stop/expiry semantics."""
    entry_position = signal_position + config.entry_lag_sessions
    expiry_position = entry_position + config.holding_sessions + 1
    entry_price = _finite_price(primary.iloc[entry_position]["Open"], "entry open")
    target_price = entry_price * (1 + config.profit_target)
    stop_price = entry_price * (1 + config.stop_loss)

    for position in range(entry_position, expiry_position):
        row = primary.iloc[position]
        low = _finite_price(row["Low"], "holding low")
        high = _finite_price(row["High"], "holding high")
        stop_hit = low <= stop_price
        target_hit = high >= target_price
        if stop_hit:
            return CandidateTrade(
                signal_date=primary.index[signal_position].date(),
                entry_date=primary.index[entry_position].date(),
                entry_price=entry_price,
                exit_date=primary.index[position].date(),
                exit_price=stop_price,
                exit_type="stop_loss_pessimistic" if target_hit else "stop_loss",
            )
        if target_hit:
            return CandidateTrade(
                signal_date=primary.index[signal_position].date(),
                entry_date=primary.index[entry_position].date(),
                entry_price=entry_price,
                exit_date=primary.index[position].date(),
                exit_price=target_price,
                exit_type="target",
            )

    exit_price = _finite_price(primary.iloc[expiry_position]["Open"], "expiry open")
    return CandidateTrade(
        signal_date=primary.index[signal_position].date(),
        entry_date=primary.index[entry_position].date(),
        entry_price=entry_price,
        exit_date=primary.index[expiry_position].date(),
        exit_price=exit_price,
        exit_type="time_expiry",
    )


def _require_price_columns(frame: pd.DataFrame) -> None:
    missing = {"Open", "High", "Low", "Close"}.difference(frame.columns)
    if missing:
        raise ValueError("primary data lacks price columns: " + ", ".join(sorted(missing)))


def _finite_price(value: object, label: str) -> float:
    price = float(value)
    if not math.isfinite(price) or price <= 0:
        raise ValueError(f"{label} must be finite and positive")
    return price
