"""
COPX-011: Multi-Week Regime-Aware BB Squeeze Breakout 策略

跨資產驗證 lesson #22 在 COPX 上的有效性。將 FCX-013 的 buffered multi-week
SMA regime 過濾器疊加於 COPX-005 BB Squeeze Breakout 之上，並新增 regime BOX
上限 k_max=1.09 過濾過熱牛末。

成果（Att3 ★）：
- min(A,B) Sharpe 0.64（+42% vs COPX-007 全域最佳 0.45）
- Part A 80% WR / Sharpe 0.72；Part B 50% WR / Sharpe 0.64
- 跨資產發現：商品/礦業 ETF（COPX）vs 個股（FCX）regime 結構差異——
  ETF 需上下限 BOX，個股單純下限即可
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_011_regime_breakout.config import (
    COPX011Config,
    create_default_config,
)
from trading.experiments.copx_011_regime_breakout.signal_detector import (
    COPX011RegimeBreakoutDetector,
)


class COPX011RegimeBreakoutStrategy(ExecutionModelStrategy):
    """COPX-011：多週期 regime 過濾 BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX011RegimeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX011Config):
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
