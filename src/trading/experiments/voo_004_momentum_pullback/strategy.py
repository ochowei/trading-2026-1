"""
VOO-004: Momentum Breakout Pullback Continuation 策略
串接 VOO-004 config → signal detector → 執行模型回測引擎。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.voo_004_momentum_pullback.config import (
    VOO004Config,
    create_default_config,
)
from trading.experiments.voo_004_momentum_pullback.signal_detector import (
    VOO004SignalDetector,
)


class VOO004MomentumPullbackStrategy(ExecutionModelStrategy):
    """VOO-004：Momentum Breakout Pullback Continuation 策略（含成交模型）"""

    slippage_pct: float = 0.001  # 0.1% (VOO 流動性佳)

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VOO004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VOO004Config):
            print(
                f"  Donchian: {config.donchian_period} 日新高，近 "
                f"{config.breakout_recency_days} 日內 breakout"
            )
            print(f"  趨勢過濾: Close > SMA({config.sma_trend_period})")
            if config.require_above_sma_long:
                print(f"  長期趨勢過濾: Close > SMA({config.sma_long_period})")
            print(
                f"  淺回檔範圍: {config.pullback_max:.1%} ~ {config.pullback_min:.1%}"
                f"（相對近 {config.pullback_lookback} 日高點）"
            )
            print(
                f"  RSI({config.rsi_period}) 中性區: [{config.rsi_min:.0f}, {config.rsi_max:.0f}]"
            )
            print(f"  多頭 K 棒: Close > Open = {config.bullish_close_required}")
            if config.require_atr_ratio:
                print(f"  ATR(5)/ATR(20) >= {config.atr_ratio_min:.2f}")
            print(f"  冷卻期: {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
