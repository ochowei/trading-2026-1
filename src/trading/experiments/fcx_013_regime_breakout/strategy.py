"""
FCX-013: Multi-Week Regime-Aware BB Squeeze Breakout 策略

跨資產驗證 lesson #22 在 FCX 上的有效性。將 TSLA-015 / NVDA-012 的 buffered
multi-week SMA regime 過濾器疊加於 FCX-004 BB Squeeze Breakout 之上，目標
改善 FCX-004 的嚴重 A/B 失衡（cum 89% / 訊號 3.83:1）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_013_regime_breakout.config import (
    FCX013Config,
    create_default_config,
)
from trading.experiments.fcx_013_regime_breakout.signal_detector import (
    FCX013RegimeBreakoutDetector,
)


class FCX013RegimeBreakoutStrategy(ExecutionModelStrategy):
    """FCX-013：多週期 regime 過濾 BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX013RegimeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX013Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" ≥ {config.sma_regime_ratio_min}"
                f" × SMA({config.sma_regime_long})"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
