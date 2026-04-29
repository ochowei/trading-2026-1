"""
FXI-012: Momentum Breakout Pullback Continuation Strategy
(FXI 動量突破回檔連續進場策略)

進場條件（六項 — Att3 最終）：
    1. 近 5 日內曾創 20 日 Donchian 新高
    2. Close > SMA(50)
    3. SMA(50) slope 正（今日 > 60 日前）
    4. 5 日高點回檔 -2% ~ -5%
    5. RSI(14) ∈ [45, 58]
    6. 冷卻 10 天

出場：
    TP +4.0% / SL -3.5% / 15 天 / 成交模型
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_012_momentum_pullback.config import (
    FXI012Config,
    create_default_config,
)
from trading.experiments.fxi_012_momentum_pullback.signal_detector import (
    FXI012SignalDetector,
)


class FXI012Strategy(ExecutionModelStrategy):
    """FXI-012：Donchian 動量突破回檔連續進場"""

    slippage_pct: float = 0.0015  # 0.15%（單一國家 EM ETF 標準）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI012Config):
            print(
                f"  Donchian 新高: {config.donchian_period} 日新高 "
                f"(近 {config.breakout_recency_days} 日內)"
            )
            print(f"  趨勢過濾: Close > SMA({config.sma_trend_period})")
            if config.require_sma20_above_sma50:
                print(
                    f"  黃金排列: SMA({config.sma_short_period}) > SMA({config.sma_trend_period})"
                )
            if config.require_sma_slope_positive:
                print(
                    f"  SMA slope 正: SMA({config.sma_trend_period})[今日] > "
                    f"SMA({config.sma_trend_period})[{config.sma_slope_lookback} 日前]"
                )
            print(
                f"  淺回檔 (Pullback): {config.pullback_lookback} 日高點回檔 "
                f"{abs(config.pullback_min):.0%}-{abs(config.pullback_max):.0%}"
            )
            print(
                f"  RSI 中性: RSI({config.rsi_period}) ∈ "
                f"[{config.rsi_min:.0f}, {config.rsi_max:.0f}]"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
