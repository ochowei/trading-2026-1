"""
CIBR-015: Momentum Breakout Pullback Continuation Strategy

策略方向：趨勢跟蹤 / 動量連續（lesson #21 跨資產假設於 sector ETF 邊界擴展試驗）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_015_momentum_pullback.config import (
    CIBR015Config,
    create_default_config,
)
from trading.experiments.cibr_015_momentum_pullback.signal_detector import (
    CIBR015SignalDetector,
)


class CIBR015Strategy(ExecutionModelStrategy):
    """CIBR-015：Momentum Breakout Pullback Continuation"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR015SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR015Config):
            print(
                f"  Donchian: {config.donchian_period} 日新高，"
                f"近 {config.breakout_recency_days} 日 freshness"
            )
            print(f"  趨勢過濾: Close > SMA({config.sma_trend_period})")
            print(
                f"  淺回檔: {config.pullback_lookback}日高點回檔"
                f" ∈ [{config.pullback_max:.1%}, {config.pullback_min:.1%}]"
            )
            print(f"  RSI({config.rsi_period}) ∈ [{config.rsi_min:.0f}, {config.rsi_max:.0f}]")
            print(f"  多頭 K 棒確認: {'是' if config.bullish_close_required else '否'}")
            if config.require_sma_regime:
                if config.require_sma_regime_box:
                    print(
                        f"  Regime BOX: SMA({config.sma_regime_short}) "
                        f"∈ [{config.sma_regime_k_min:.2f}, {config.sma_regime_k_max:.2f}]"
                        f" × SMA({config.sma_regime_long})"
                    )
                else:
                    print(
                        f"  Buffered SMA Regime: SMA({config.sma_regime_short}) "
                        f">= {config.sma_regime_k_min:.2f} × SMA({config.sma_regime_long})"
                    )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
