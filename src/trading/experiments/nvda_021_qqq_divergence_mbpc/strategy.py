"""
NVDA-021: NVDA-QQQ Cross-Asset Divergence CEILING Regime-Gated MBPC 策略

跨**策略類型**首次將 cross-asset divergence regime gate（CEILING 方向，
mirror INDA-012 / EWZ-009 outperformer-mean-reversion）應用於高波動 AI mega-cap
個股 + MBPC 框架（先前 TLT-014 / TSLA-017 為 FLOOR 方向、INDA-012 / EWZ-009 為
CEILING 方向但於 MR 框架）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_021_qqq_divergence_mbpc.config import (
    NVDA021Config,
    create_default_config,
)
from trading.experiments.nvda_021_qqq_divergence_mbpc.signal_detector import (
    NVDA021QQQDivergenceMBPCDetector,
)


class NVDA021QQQDivergenceMBPCStrategy(ExecutionModelStrategy):
    """NVDA-021：NVDA-QQQ 跨資產背離 CEILING regime gate + MBPC（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA021QQQDivergenceMBPCDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA021Config):
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
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用")
            if config.use_divergence_filter:
                print(
                    f"  跨資產背離 CEILING: NVDA - {config.benchmark_ticker}"
                    f" {config.divergence_lookback}d 報酬差 ≤ "
                    f"{config.max_relative_return:+.2%}"
                )
            else:
                print("  跨資產背離: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
