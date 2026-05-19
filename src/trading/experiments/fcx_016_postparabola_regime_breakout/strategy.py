"""
FCX-016: Post-Parabolic Long-Horizon Regime-Gated VIX-FLOOR BB Squeeze
         Breakout Strategy

跨資產移植 URA-014 Att1 ★ SUCCESS 的「post-parabolic 長窗 prior-Nd-return
CEILING」regime gate（lesson #19 family v3）至 FCX-015 Att2（FCX 全域最優
min(A,B)† = Part A Sharpe 1.43）框架之上。predict→confirm 前置分析已判定
FCX 唯一殘餘 binding Part A SL 2021-11-11 之 prior-Nd-return 與全部 winners
完全 interleaved 且方向 INVERTED（URA SL Ret60 最高 / FCX SL 偏低，FCX 最大
prior-60d run-ups 全為 winners）→ 預測 documented-failure，三次迭代確認並
記錄 lesson #19 family v3 不可移植 copper-supercycle commodity miner 之
新跨資產規則。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_016_postparabola_regime_breakout.config import (
    FCX016Config,
    create_default_config,
)
from trading.experiments.fcx_016_postparabola_regime_breakout.signal_detector import (
    FCX016PostparabolaRegimeBreakoutDetector,
)


class FCX016PostparabolaRegimeBreakoutStrategy(ExecutionModelStrategy):
    """FCX-016：Post-Parabolic Regime Gate + VIX-FLOOR BB Squeeze Breakout"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX016PostparabolaRegimeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX016Config):
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
            print(f"  VIX 過濾 (VIX FLOOR): VIX > {config.vix_low_threshold:.1f}")
            print(
                f"  Post-parabolic 長窗 prior-return CEILING: "
                f"prior {config.runup_lookback}d return <= {config.runup_ceiling:.2%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
