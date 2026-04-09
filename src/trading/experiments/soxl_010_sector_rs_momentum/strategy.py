"""
SOXL-010: Semiconductor Sector RS Momentum Pullback 策略

在半導體板塊（SOXX）相對大盤（SPY）展現超額表現時買入 SOXL 回調，
捕捉板塊動量的 3x 槓桿放大效果。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_010_sector_rs_momentum.config import (
    SOXLSectorRSConfig,
    create_default_config,
)
from trading.experiments.soxl_010_sector_rs_momentum.signal_detector import (
    SOXLSectorRSDetector,
)


class SOXLSectorRSStrategy(ExecutionModelStrategy):
    """SOXL-010: Semiconductor Sector RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXLSectorRSDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SOXLSectorRSConfig):
            print(
                f"  板塊 RS (Sector RS): {config.sector_ticker} - {config.benchmark_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
