"""COPX-014: COPX-GLD Cross-Asset Divergence Regime-Gated BB Squeeze Breakout 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_014_gld_divergence_breakout.config import (
    COPX014Config,
    create_default_config,
)
from trading.experiments.copx_014_gld_divergence_breakout.signal_detector import (
    COPX014SignalDetector,
)


class COPX014GldDivergenceBreakoutStrategy(ExecutionModelStrategy):
    """COPX-014：BB Squeeze Breakout + regime BOX + COPX-GLD divergence gate（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15%（同 COPX-011，ETF 中等流動性）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX014Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime BOX: {config.sma_regime_ratio_min:.2f} ≤ "
                f"SMA({config.sma_regime_short})/SMA({config.sma_regime_long})"
                f" ≤ {config.sma_regime_ratio_max:.2f}"
            )
            print(
                f"  Cross-asset divergence gate: COPX vs {config.benchmark_ticker}"
                f" {config.divergence_lookback}d return diff >= {config.min_relative_return:+.1%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
