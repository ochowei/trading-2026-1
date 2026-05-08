"""
TSM-012: Volume-Confirmed RS Momentum Pullback 策略

延伸 TSM-008 RS 動量回調框架，加入 signal-day volume ratio 過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_012_volume_confirmed_rs_pullback.config import (
    TSMVolumeConfirmedConfig,
    create_default_config,
)
from trading.experiments.tsm_012_volume_confirmed_rs_pullback.signal_detector import (
    TSMVolumeConfirmedDetector,
)


class TSMVolumeConfirmedStrategy(ExecutionModelStrategy):
    """TSM-012：Volume-Confirmed RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMVolumeConfirmedDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMVolumeConfirmedConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): TSM - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            if config.vol_ratio_min > 0.0:
                print(
                    f"  成交量下限 (Volume floor): Volume / SMA(Volume,"
                    f" {config.volume_avg_window}) >= {config.vol_ratio_min:.2f}x"
                )
            if config.vol_ratio_max < 999.0:
                print(
                    f"  成交量上限 (Volume ceiling): Volume / SMA(Volume,"
                    f" {config.volume_avg_window}) <= {config.vol_ratio_max:.2f}x"
                )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
