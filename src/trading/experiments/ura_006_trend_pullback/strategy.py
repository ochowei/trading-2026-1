"""
URA-006: 相對強度回調買入策略
(URA Relative Strength Pullback Entry Strategy)

URA 相對 XLE 有超額表現時買入回調，
參考 TSM-008 成功的 RS 進場模式。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_006_trend_pullback.config import (
    URATrendPullbackConfig,
    create_default_config,
)
from trading.experiments.ura_006_trend_pullback.signal_detector import (
    URATrendPullbackDetector,
)


class URATrendPullbackStrategy(ExecutionModelStrategy):
    """URA-006：相對強度回調買入（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15%

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URATrendPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URATrendPullbackConfig):
            print(
                f"  相對強度 (RS): URA - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(f"  趨勢位置 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  回調範圍 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
