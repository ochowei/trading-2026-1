"""
NVDA-017: Signal-Day 5d Return CEILING on Multi-Week Regime-Aware MBPC 策略

Lesson #19 family v10/v12 cross-asset port from TSM-011 Att3：repo 首次將
「rally exhaustion 5d ceiling」假設移植至 MBPC 框架（先前僅於 TSM-008 RS
Momentum 框架驗證）。三次迭代均失敗，REJECT 跨資產假設於高波動 AI 個股
+ MBPC 框架。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_017_signal_day_filter.config import (
    NVDA017Config,
    create_default_config,
)
from trading.experiments.nvda_017_signal_day_filter.signal_detector import (
    NVDA017SignalDayFilterDetector,
)


class NVDA017SignalDayFilterStrategy(ExecutionModelStrategy):
    """NVDA-017：MBPC + 訊號日 5 日報酬 CEILING 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA017SignalDayFilterDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA017Config):
            print(
                f"  Donchian: {config.donchian_period} 日新高，近 "
                f"{config.breakout_recency_days} 日內 breakout"
            )
            print(f"  趨勢過濾 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" >= {config.sma_regime_ratio_min}"
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
                    f" <= {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用")
            if config.ret_5d_max < 999:
                print(
                    f"  訊號日 5 日報酬 CEILING: "
                    f"<= {config.ret_5d_max:.3f}"
                    f"（rally exhaustion 過濾）"
                )
            else:
                print("  訊號日 5 日報酬 CEILING: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
