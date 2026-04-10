"""
COPX-008 Att3: Donchian Channel Breakout 策略

Att1-2 驗證 RS 動量回調在銅礦 ETF 無效後，
Att3 改用 Donchian 通道突破（趨勢跟蹤策略）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_008_rs_momentum.config import (
    COPX008Config,
    create_default_config,
)
from trading.experiments.copx_008_rs_momentum.signal_detector import (
    COPX008SignalDetector,
)


class COPX008Strategy(ExecutionModelStrategy):
    """COPX-008: Donchian Channel Breakout（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% for commodity miners

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX008SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX008Config):
            print(f"  Donchian 突破: Close > {config.donchian_period}日最高價")
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
