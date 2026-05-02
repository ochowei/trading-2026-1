"""
FCX-014: Multi-Period Direction-Filter Regime BB Squeeze Breakout 策略

跨資產驗證 lesson #19 family ceiling 維度於 BB Squeeze Breakout 框架。將
TSM-011 Att3 RS Momentum 框架成功的 5d return ceiling 概念跨策略移植至
FCX-013 Att3 BB Squeeze Breakout 之上，目標進一步突破 FCX-013 的 min(A,B)
0.55 並改善 A/B 累計報酬差距 44.0%。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_014_breakout_ceiling.config import (
    FCX014Config,
    create_default_config,
)
from trading.experiments.fcx_014_breakout_ceiling.signal_detector import (
    FCX014BreakoutCeilingDetector,
)


class FCX014BreakoutCeilingStrategy(ExecutionModelStrategy):
    """FCX-014：訊號日方向過濾 + lesson #22 regime BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX014BreakoutCeilingDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX014Config):
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
            ceiling = config.max_signal_day_3d_return
            ceiling_str = "停用" if ceiling is None else f"<= {ceiling:.2%}"
            print(f"  訊號日 3 日報酬上限 (3d Ceiling): {ceiling_str}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
