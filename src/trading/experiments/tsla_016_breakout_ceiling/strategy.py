"""
TSLA-016: Multi-Period Direction-Filter Regime BB Squeeze Breakout 策略

直接驗證 FCX-014 提出的明確跨資產假設——將 lesson #19 family 的 signal-day
return CEILING 維度跨資產移植至 TSLA-015 Att3 BB Squeeze Breakout 框架。
本實驗為 repo 第 4 個 lesson #19 family 框架類型驗證（MR / RS / FCX BB Squeeze
之後第 4 個），首次於高波動 AI 個股（TSLA 3.72% 日波動）測試 ceiling 維度。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_016_breakout_ceiling.config import (
    TSLA016Config,
    create_default_config,
)
from trading.experiments.tsla_016_breakout_ceiling.signal_detector import (
    TSLA016BreakoutCeilingDetector,
)


class TSLA016BreakoutCeilingStrategy(ExecutionModelStrategy):
    """TSLA-016：訊號日方向過濾 + lesson #22 regime BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA016BreakoutCeilingDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA016Config):
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
            ceiling_3d = config.max_signal_day_3d_return
            ceiling_3d_str = "停用" if ceiling_3d is None else f"<= {ceiling_3d:.2%}"
            print(f"  訊號日 3 日報酬上限 (3d Ceiling): {ceiling_3d_str}")
            ceiling_5d = config.max_signal_day_5d_return
            ceiling_5d_str = "停用" if ceiling_5d is None else f"<= {ceiling_5d:.2%}"
            print(f"  訊號日 5 日報酬上限 (5d Ceiling): {ceiling_5d_str}")
            ceiling_1d = config.max_signal_day_1d_return
            ceiling_1d_str = "停用" if ceiling_1d is None else f"<= {ceiling_1d:.2%}"
            print(f"  訊號日 1 日報酬上限 (1d Ceiling): {ceiling_1d_str}")
            if config.use_vol_regime:
                print(
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 停用 (TSLA-015 Att3 ablation 確認冗餘)")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
