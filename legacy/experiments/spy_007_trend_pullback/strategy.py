"""
SPY-007: Trend Pullback to SMA(50)
(SPY Trend Following Strategy)

使用 SMA 黃金交叉 + 回測 SMA(50) + 反彈作為順勢進場訊號，
搭配 ExecutionModelBacktester 成交模型。
"""

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.core.followup_cutover import DataAccessParityOutputs
from trading.core.sleeve_engine import (
    CANONICAL_SLEEVE_ENGINE_VERSION,
    DEFAULT_BASE_COST_POLICY,
    DEFAULT_STRESS_COST_POLICY,
    CandidateTrade,
    CanonicalSleeveInput,
)
from trading.experiments.spy_007_trend_pullback.config import (
    SPY007TrendPullbackConfig,
    create_default_config,
)
from trading.experiments.spy_007_trend_pullback.signal_detector import (
    SPY007TrendPullbackDetector,
)
from trading.market_data import MarketDataBundle, MarketDataRequirement, MarketDataSeries
from trading.research_data import (
    ExperimentTrialDeclaration,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
)


@dataclass(frozen=True)
class _BundleExecution:
    indicators: pd.DataFrame
    parts: dict[str, dict[str, object]]
    signal_dates: tuple[date, ...]
    trades: tuple[Mapping[str, object], ...]


class SPY007TrendPullbackStrategy(ExecutionModelStrategy):
    """SPY Trend Pullback to SMA(50) (SPY-007)"""

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        """Declare the complete primary-only market-data dependency."""
        config = self.create_config()
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
        """Capture source and requirement identity without resolving market data."""
        config = self.create_config()
        return store.capture(
            resolved_config={
                "config": asdict(config),
                "market_data_requirements": self.market_data_requirements(),
            },
            sources={
                "strategy": Path(__file__),
                "detector": Path(__file__).with_name("signal_detector.py"),
                "backtester": Path(__file__).parents[3]
                / "src"
                / "trading"
                / "core"
                / "execution_backtester.py",
            },
            execution_engine_version=CANONICAL_SLEEVE_ENGINE_VERSION,
            dependency_versions={"pandas": pd.__version__},
            base_cost_policy=DEFAULT_BASE_COST_POLICY,
            stress_cost_policy=DEFAULT_STRESS_COST_POLICY,
        )

    def declare_experiment_trial(self) -> ExperimentTrialDeclaration:
        """Declare the stable family and hypothesis for formal trial registration."""
        return ExperimentTrialDeclaration(
            family="SPY:trend-pullback",
            hypothesis="SPY entries after a confirmed uptrend pull back and rebound.",
        )

    def run_with_bundle(self, bundle: MarketDataBundle) -> dict[str, object]:
        """Run the SPY-007 detector and execution model without provider capabilities."""
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
        """Expose canonical indicator, signal, and trade outputs for migration parity."""
        execution = self._execute_bundle(bundle)
        return DataAccessParityOutputs(
            indicators=execution.indicators,
            signals=execution.signal_dates,
            trades=execution.trades,
        )

    def _execute_bundle(self, bundle: MarketDataBundle) -> _BundleExecution:
        config = self.create_config()
        declared_series = tuple(item.series for item in self.market_data_requirements())
        if tuple(bundle) != declared_series:
            raise ValueError("SPY-007 bundle keys do not match its declared requirements")
        frame = bundle[declared_series[0]]
        detector = self.create_detector()
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
        return _BundleExecution(
            indicators=indicators,
            parts=parts,
            signal_dates=tuple(signal_dates),
            trades=tuple(trades),
        )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPY007TrendPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPY007TrendPullbackConfig):
            print(f"  SMA 短線: {config.sma_short_period}")
            print(f"  SMA 中線: {config.sma_mid_period}")
            print(f"  SMA 長線: {config.sma_long_period}")
            print(f"  收盤位置: >= {config.close_position_threshold:.0%} of day range")
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)


def _candidate_from_trade(trade: Mapping[str, object]) -> CandidateTrade | None:
    """Convert one filled execution-model trade into canonical candidate input."""
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
