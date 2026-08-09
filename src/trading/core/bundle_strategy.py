"""Shared primary-only execution seams for snapshot-aware strategies."""

from __future__ import annotations

import hashlib
import inspect
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_cutover import DataAccessParityOutputs
from trading.core.followup_data import DeclaredAuxiliaryData, FollowupDataBundle
from trading.core.sleeve_engine import (
    CANONICAL_SLEEVE_ENGINE_VERSION,
    DEFAULT_BASE_COST_POLICY,
    DEFAULT_STRESS_COST_POLICY,
    CandidateTrade,
    CanonicalSleeveInput,
)
from trading.market_data import (
    AvailabilityPolicy,
    MarketDataAvailabilityError,
    MarketDataBundle,
    MarketDataCoveragePolicy,
    MarketDataRequirement,
    MarketDataSeries,
    PrimaryUSSessionCalendar,
)
from trading.research_data import (
    ExperimentTrialDeclaration,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
)


@dataclass(frozen=True)
class BundleExecution:
    """Detector and execution outputs produced from one verified bundle."""

    indicators: pd.DataFrame
    parts: dict[str, dict[str, object]]
    signal_dates: tuple[date, ...]
    trades: tuple[Mapping[str, object], ...]


class PrimaryBundleStrategyMixin:
    """Provide the formal contract for a single declared primary series.

    The concrete strategy supplies ``create_config``, ``create_detector`` and
    ``create_backtester`` through ``ExecutionModelStrategy``.  It also declares
    ``bundle_trial_family`` and ``bundle_trial_hypothesis`` as class attributes.
    """

    bundle_trial_family: str
    bundle_trial_hypothesis: str = ""

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        """Declare exactly one adjusted-daily primary dependency."""
        config = self.create_config()
        if len(config.tickers) != 1:
            raise ValueError("primary-only bundle strategies require exactly one ticker")
        return (
            MarketDataRequirement(
                MarketDataSeries.yahoo_adjusted_daily(config.tickers[0]),
                date.fromisoformat(config.data_start),
                role="primary",
            ),
        )

    def capture_research_definition(
        self,
        store: ResearchDefinitionStore,
    ) -> ResearchDefinitionSnapshot:
        """Capture config, implementation, and shared bundle-runner identity."""
        config = self.create_config()
        strategy_path = Path(inspect.getfile(type(self))).resolve()
        detector_path = strategy_path.with_name("signal_detector.py")
        backtester = self.create_backtester(config)
        backtester_path = Path(inspect.getfile(type(backtester))).resolve()
        return store.capture(
            resolved_config={
                "config": asdict(config),
                "market_data_requirements": self.market_data_requirements(),
            },
            sources={
                "strategy": strategy_path,
                "detector": detector_path,
                "backtester": backtester_path,
                "bundle_executor": Path(__file__).resolve(),
            },
            execution_engine_version=CANONICAL_SLEEVE_ENGINE_VERSION,
            dependency_versions={"pandas": pd.__version__},
            base_cost_policy=DEFAULT_BASE_COST_POLICY,
            stress_cost_policy=DEFAULT_STRESS_COST_POLICY,
        )

    def declare_experiment_trial(self) -> ExperimentTrialDeclaration:
        """Declare the stable family and hypothesis for formal trial history."""
        family = getattr(self, "bundle_trial_family", None)
        hypothesis = getattr(self, "bundle_trial_hypothesis", "")
        if not isinstance(family, str) or not family.strip():
            raise ValueError("primary-only bundle strategies require a trial family")
        return ExperimentTrialDeclaration(family=family, hypothesis=hypothesis)

    def run_with_bundle(self, bundle: MarketDataBundle) -> dict[str, object]:
        """Run detector and execution model without provider capabilities."""
        execution = self._execute_bundle(bundle)
        candidates = [
            candidate
            for trade in execution.trades
            if (candidate := _candidate_from_trade(trade)) is not None
        ]
        canonical_signals = execution.signal_dates
        sleeve_input = CanonicalSleeveInput(
            calendar=tuple(pd.Timestamp(value).normalize() for value in execution.indicators.index),
            close_prices=execution.indicators["Close"].copy(deep=True),
            candidates=tuple(candidates),
            raw_signals=canonical_signals,
            legacy_signals=canonical_signals,
            legacy_candidates=tuple(candidates),
            initial_capital=1.0,
        )
        config = self.create_config()
        return {
            "metadata": {
                "experiment": config.name,
                "data_cutoff": execution.indicators.index[-1].date().isoformat(),
            },
            "part_a": execution.parts["Part A (In-Sample)"],
            "part_b": execution.parts["Part B (Out-of-Sample)"],
            "part_c": execution.parts["Part C (Live)"],
            "canonical_sleeve_input": sleeve_input,
        }

    def run_for_parity(self, bundle: MarketDataBundle) -> DataAccessParityOutputs:
        """Expose ordered indicators, signals, and fills for migration parity."""
        execution = self._execute_bundle(bundle)
        return DataAccessParityOutputs(
            indicators=execution.indicators,
            signals=execution.signal_dates,
            trades=execution.trades,
        )

    def _execute_bundle(self, bundle: MarketDataBundle) -> BundleExecution:
        config: ExperimentConfig = self.create_config()
        declared_series = tuple(item.series for item in self.market_data_requirements())
        if tuple(bundle) != declared_series:
            raise ValueError(f"{config.name} bundle keys do not match its declared requirements")
        frame = bundle[declared_series[0]]
        detector: BaseSignalDetector = self.create_detector()
        backtester = self.create_backtester(config)
        indicators = detector.compute_indicators(frame)
        parts: dict[str, dict[str, object]] = {}
        signal_dates: list[date] = []
        trades: list[Mapping[str, object]] = []

        for label, start, end in config.get_parts():
            resolved_end = end or indicators.index[-1].strftime("%Y-%m-%d")
            part = indicators.loc[start:resolved_end].copy()
            if part.empty:
                result = backtester._empty_result()
            else:
                signaled = detector.detect_signals(part)
                signal_dates.extend(item.date() for item in signaled.index[signaled["Signal"]])
                result = backtester.run(signaled)
                trades.extend(result["trades"])
            result["backtest_period"] = {"start": start, "end": resolved_end}
            parts[label] = result
        return BundleExecution(
            indicators=indicators,
            parts=parts,
            signal_dates=tuple(signal_dates),
            trades=tuple(trades),
        )


class AuxiliaryBundleStrategyMixin(PrimaryBundleStrategyMixin):
    """Extend the primary contract with declared historical auxiliary series."""

    bundle_auxiliary_max_lag_sessions: int = 3

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        config = self.create_config()
        if len(config.tickers) != 1:
            raise ValueError("auxiliary bundle strategies require exactly one primary ticker")
        detector = self.create_detector()
        if not isinstance(detector, DeclaredAuxiliaryData):
            raise TypeError("auxiliary bundle strategies require DeclaredAuxiliaryData")
        symbols = tuple(detector.auxiliary_symbols())
        if len(set(symbols)) != len(symbols):
            raise ValueError("auxiliary declarations must be unique")
        if config.tickers[0] in symbols:
            raise ValueError("primary ticker cannot also be auxiliary")
        primary = MarketDataRequirement(
            MarketDataSeries.yahoo_adjusted_daily(config.tickers[0]),
            date.fromisoformat(config.data_start),
            role="primary",
        )
        auxiliary_policy = AvailabilityPolicy(
            publication_lag_sessions=1,
            max_observation_lag_sessions=self.bundle_auxiliary_max_lag_sessions,
            publication_time_known=False,
        )
        return (
            primary,
            *(
                MarketDataRequirement(
                    MarketDataSeries.yahoo_adjusted_daily(symbol),
                    date.fromisoformat(config.data_start),
                    role="auxiliary",
                    availability_policy=auxiliary_policy,
                    coverage_policy=MarketDataCoveragePolicy.provider_observations(),
                )
                for symbol in symbols
            ),
        )

    def _execute_bundle(self, bundle: MarketDataBundle) -> BundleExecution:
        config: ExperimentConfig = self.create_config()
        requirements = self.market_data_requirements()
        declared_series = tuple(item.series for item in requirements)
        if tuple(bundle) != declared_series:
            raise ValueError(f"{config.name} bundle keys do not match its declared requirements")
        primary_requirement = requirements[0]
        primary_series = primary_requirement.series
        calendar = PrimaryUSSessionCalendar()
        first_session = calendar.session_on_or_after(primary_requirement.history_start)
        frame = bundle[primary_series].loc[pd.Timestamp(first_session) :]
        detector = self.create_detector()
        if not isinstance(detector, DeclaredAuxiliaryData):  # pragma: no cover - declaration guard
            raise TypeError("auxiliary bundle strategy detector does not declare auxiliary data")
        auxiliary_frames: dict[str, pd.DataFrame] = {}
        for requirement in requirements[1:]:
            aligned = bundle[requirement.series]
            if not pd.DatetimeIndex(frame.index).isin(aligned.index).all():
                raise MarketDataAvailabilityError(
                    f"auxiliary series {requirement.series.symbol} does not cover every "
                    "primary decision session"
                )
            auxiliary_frames[requirement.series.symbol] = aligned
        detector.bind_auxiliary_data(
            FollowupDataBundle(
                primary_symbol=config.tickers[0],
                primary=frame,
                auxiliary=auxiliary_frames,
                identity=_bundle_identity(bundle, declared_series),
            )
        )
        backtester = self.create_backtester(config)
        indicators = detector.compute_indicators(frame)
        parts: dict[str, dict[str, object]] = {}
        signal_dates: list[date] = []
        trades: list[Mapping[str, object]] = []

        for label, start, end in config.get_parts():
            resolved_end = end or indicators.index[-1].strftime("%Y-%m-%d")
            part = indicators.loc[start:resolved_end].copy()
            if part.empty:
                result = backtester._empty_result()
            else:
                signaled = detector.detect_signals(part)
                signal_dates.extend(item.date() for item in signaled.index[signaled["Signal"]])
                result = backtester.run(signaled)
                trades.extend(result["trades"])
            result["backtest_period"] = {"start": start, "end": resolved_end}
            parts[label] = result
        return BundleExecution(
            indicators=indicators,
            parts=parts,
            signal_dates=tuple(signal_dates),
            trades=tuple(trades),
        )


def _candidate_from_trade(trade: Mapping[str, object]) -> CandidateTrade | None:
    """Convert one filled execution-model trade into canonical sleeve input."""
    required = ("date", "entry_date", "entry", "exit_date", "exit")
    if any(trade.get(field) is None for field in required):
        return None
    return CandidateTrade(
        signal_date=date.fromisoformat(str(trade["date"])),
        entry_date=date.fromisoformat(str(trade["entry_date"])),
        entry_price=float(trade["entry"]),
        exit_date=date.fromisoformat(str(trade["exit_date"])),
        exit_price=float(trade["exit"]),
        exit_type=str(trade.get("exit_type")) if trade.get("exit_type") else None,
    )


def _bundle_identity(
    bundle: MarketDataBundle,
    series: tuple[MarketDataSeries, ...],
) -> str:
    digest = hashlib.sha256()
    for item in series:
        digest.update(item.symbol.encode("utf-8"))
        digest.update(b"\0")
        digest.update(
            bundle[item]
            .to_csv(index=True, date_format="%Y-%m-%d", float_format="%.17g")
            .encode("utf-8")
        )
        digest.update(b"\0")
    return digest.hexdigest()
