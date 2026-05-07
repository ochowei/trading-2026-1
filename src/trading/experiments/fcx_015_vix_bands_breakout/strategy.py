"""
FCX-015: VIX BANDS Filter on BB Squeeze Breakout Strategy

跨資產驗證 lesson #24 family BANDS 變體於 BB Squeeze Breakout 框架。將
XBI-017 Pullback MR 框架成功的 ^VIX BANDS regime gate 跨策略移植至
FCX-014 Att1 BB Squeeze Breakout 之上，目標進一步突破 FCX-014 的 min(A,B)
0.64 並改善 A/B 累計報酬差距 52.5%。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_015_vix_bands_breakout.config import (
    FCX015Config,
    create_default_config,
)
from trading.experiments.fcx_015_vix_bands_breakout.signal_detector import (
    FCX015VixBandsBreakoutDetector,
)


class FCX015VixBandsBreakoutStrategy(ExecutionModelStrategy):
    """FCX-015：VIX BANDS + BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX015VixBandsBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX015Config):
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
            mode = config.vix_filter_mode
            if mode == "bands_exclude_mid":
                vix_str = (
                    f"BANDS exclude mid: VIX <= {config.vix_low_threshold:.1f}"
                    f" OR VIX > {config.vix_high_threshold:.1f}"
                )
            elif mode == "floor":
                vix_str = f"FLOOR: VIX > {config.vix_low_threshold:.1f}"
            elif mode == "cap":
                vix_str = f"CAP: VIX <= {config.vix_high_threshold:.1f}"
            elif mode == "bands_keep_mid":
                vix_str = (
                    f"BANDS keep mid: {config.vix_low_threshold:.1f}"
                    f" < VIX <= {config.vix_high_threshold:.1f}"
                )
            else:
                vix_str = "停用"
            print(f"  VIX 過濾 (VIX filter): {vix_str}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
