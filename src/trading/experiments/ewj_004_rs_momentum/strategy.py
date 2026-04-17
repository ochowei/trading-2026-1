"""
EWJ-004: Relative Strength Momentum Pullback Strategy

使用 EWJ vs EFA 20日相對強度 + 5日短期回調 + SMA(50) 趨勢確認作為進場條件。
出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewj_004_rs_momentum.config import (
    EWJ004Config,
    create_default_config,
)
from trading.experiments.ewj_004_rs_momentum.signal_detector import (
    EWJ004SignalDetector,
)


class EWJ004Strategy(ExecutionModelStrategy):
    """EWJ-004: RS 動量回調"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWJ004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWJ004Config):
            print(f"  參考基準: {config.reference_ticker}")
            print(
                f"  相對強度: {config.relative_strength_period}日 EWJ-"
                f"{config.reference_ticker} >= {config.relative_strength_min:.1%}"
            )
            print(
                f"  回撤範圍: {config.pullback_lookback}日高點回撤 "
                f"{config.pullback_min:.1%} ~ {config.pullback_max:.1%}"
            )
            print(f"  SMA 趨勢: SMA({config.sma_trend_period})")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
