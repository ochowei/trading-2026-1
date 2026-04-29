"""
IWM-014: Momentum Breakout Pullback Continuation 策略

跨資產驗證 lesson #21 在小型股寬基 ETF 上的有效性。將 VOO-004 Att3 MBPC
框架按 1.5x 波動度比例縮放至 IWM 之上，探索 repo 中相對較少使用的「動量
延續」方向。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_014_momentum_pullback.config import (
    IWM014Config,
    create_default_config,
)
from trading.experiments.iwm_014_momentum_pullback.signal_detector import (
    IWM014SignalDetector,
)


class IWM014MomentumPullbackStrategy(ExecutionModelStrategy):
    """IWM-014：Momentum Breakout Pullback Continuation 策略（含成交模型）"""

    slippage_pct: float = 0.001  # 0.1% (IWM 流動性高)

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM014Config):
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
            if config.require_sma_regime:
                print(
                    f"  Regime BOX: SMA({config.sma_regime_short})"
                    f"/SMA({config.sma_regime_long}) ∈ "
                    f"[{config.sma_regime_ratio_min:.2f}, "
                    f"{config.sma_regime_ratio_max:.2f}]"
                )
            print(f"  冷卻期: {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
