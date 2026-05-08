"""
NVDA-020: Volatility-Acceleration Band Filter on Regime-Aware MBPC

在 NVDA-013 Att3 多週期 regime-aware MBPC 框架（min(A,B) 0.55 全域最佳）上
疊加入場日 ATR(5)/ATR(20) ratio BAND 過濾（CIBR-014 / FXI-014 跨資產移植）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_020_atr_band_mbpc.config import (
    NVDA020Config,
    create_default_config,
)
from trading.experiments.nvda_020_atr_band_mbpc.signal_detector import (
    NVDA020ATRBandMBPCDetector,
)


class NVDA020ATRBandMBPCStrategy(ExecutionModelStrategy):
    """NVDA-020：Vol-Acceleration Band Filter on Regime-Aware MBPC（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA020ATRBandMBPCDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA020Config):
            print(
                f"  Donchian: {config.donchian_period} 日新高，近 "
                f"{config.breakout_recency_days} 日內 breakout"
            )
            print(f"  趨勢過濾 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" ≥ {config.sma_regime_ratio_min}"
                f" × SMA({config.sma_regime_long})"
            )
            print(
                f"  淺回檔範圍: {config.pullback_max:.1%} ~ {config.pullback_min:.1%}"
                f"（相對近 {config.pullback_lookback} 日高點）"
            )
            print(
                f"  RSI({config.rsi_period}) 中性區: [{config.rsi_min:.0f}, {config.rsi_max:.0f}]"
            )
            print(f"  多頭 K 棒: Close > Open = {config.bullish_close_required}")
            if config.use_vol_regime:
                print(
                    f"  多週期波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  多週期波動 regime: 已停用")
            if config.use_atr_band:
                print(
                    f"  入場日 ATR ratio BAND: ATR({config.atr_band_short})"
                    f" / ATR({config.atr_band_long})"
                    f" ∈ ({config.atr_band_floor}, {config.atr_band_ceiling}]"
                )
            else:
                print("  入場日 ATR ratio BAND: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
