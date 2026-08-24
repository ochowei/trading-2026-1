"""SPY-010 qualification baseline for the SPY trend-pullback family."""

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
from trading.experiments.spy_010_trend_pullback_baseline.config import (
    SPY010TrendPullbackBaselineConfig,
    create_default_config,
)
from trading.experiments.spy_010_trend_pullback_baseline.signal_detector import (
    SPY010TrendPullbackBaselineDetector,
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


class SPY010TrendPullbackBaselineStrategy(ExecutionModelStrategy):
    """SPY-007 Attempt 2 的獨立 qualification family baseline。"""

    def market_data_requirements(self) -> tuple[MarketDataRequirement, ...]:
        """宣告完整且僅含 SPY 的 primary market-data dependency。"""
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
        """捕捉 baseline 的 exact source、config 與 data requirement identity。"""
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
        """將 comparator 放入 selected trial 的相同 formal family。"""
        return ExperimentTrialDeclaration(
            family="SPY:trend-pullback",
            hypothesis=(
                "SPY trend-pullback family baseline reproducing SPY-007 Attempt 2 "
                "without ClosePos confirmation."
            ),
        )

    def run_with_bundle(self, bundle: MarketDataBundle) -> dict[str, object]:
        """在無 provider capability 下執行 baseline 與 canonical sleeve。"""
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
        """提供 deterministic indicator、signal 與 trade outputs。"""
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
            raise ValueError("SPY-010 bundle keys do not match its declared requirements")
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
        return SPY010TrendPullbackBaselineDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPY010TrendPullbackBaselineConfig):
            print(f"  SMA 短線: {config.sma_short_period}")
            print(f"  SMA 中線: {config.sma_mid_period}")
            print(f"  SMA 長線: {config.sma_long_period}")
            print("  收盤位置確認: 無 (Family baseline)")
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)


def _candidate_from_trade(trade: Mapping[str, object]) -> CandidateTrade | None:
    """將 filled execution-model trade 轉換為 canonical candidate。"""
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
