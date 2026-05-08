"""
COPX-015: ^VIX FLOOR Filter on BB Squeeze Breakout Strategy

跨資產驗證 lesson #24 family FLOOR 變體於商品/礦業 ETF 突破策略。將
FCX-015 Att2（FCX 商品/礦業單股，min(A,B) 0.64→1.43，+123%，A/B cum
gap 52.5%→7.1%）成功的 ^VIX FLOOR regime gate 跨資產移植至 COPX-011 Att3
（COPX 商品/礦業 ETF）BB Squeeze Breakout 之上，目標進一步突破 COPX-011
的 min(A,B) 0.64 並改善 A/B 累計報酬差距 66.4%。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_015_vix_bands_breakout.config import (
    COPX015Config,
    create_default_config,
)
from trading.experiments.copx_015_vix_bands_breakout.signal_detector import (
    COPX015VixBandsBreakoutDetector,
)


class COPX015VixBandsBreakoutStrategy(ExecutionModelStrategy):
    """COPX-015：^VIX FLOOR + regime BOX BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX015VixBandsBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX015Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime BOX: {config.sma_regime_ratio_min:.2f}"
                f" <= SMA({config.sma_regime_short})"
                f" / SMA({config.sma_regime_long})"
                f" <= {config.sma_regime_ratio_max:.2f}"
            )
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
