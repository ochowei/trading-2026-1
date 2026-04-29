"""
USO-024: Multi-Week Regime-Aware BB Squeeze Breakout 策略

跨資產驗證 lesson #22 在 USO 上的有效性。將 COPX-011 / FCX-013 的 buffered
multi-week SMA regime 過濾器疊加於 USO-021 BB Squeeze Breakout 之上。

USO 為 repo 第 5 次 lesson #22 試驗，**首次純單一商品 ETF（原油）驗證**。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_024_regime_breakout.config import (
    USO024Config,
    create_default_config,
)
from trading.experiments.uso_024_regime_breakout.signal_detector import (
    USO024RegimeBreakoutDetector,
)


class USO024RegimeBreakoutStrategy(ExecutionModelStrategy):
    """USO-024：多週期 regime 過濾 BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0010

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USO024RegimeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USO024Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            regime_str = (
                f"{config.sma_regime_ratio_min:.2f} ≤ SMA({config.sma_regime_short})"
                f"/SMA({config.sma_regime_long})"
            )
            if config.sma_regime_ratio_max < 99.0:
                regime_str += f" ≤ {config.sma_regime_ratio_max:.2f}"
            else:
                regime_str += " (no upper bound)"
            print(f"  趨勢 regime: {regime_str}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
