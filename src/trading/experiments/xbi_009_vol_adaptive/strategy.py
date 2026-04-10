"""
XBI-009: RSI(2) 均值回歸 + 反轉K線策略

Att3: 改用 RSI(2) 進場（SPY/DIA/IWM 最佳均值回歸框架），保留 XBI-005 驗證的 ClosePos 過濾。
RSI(2)<10 + 2日跌幅>=3.0% + ClosePos>=35%，TP+3.5%/SL-5.0%/15天。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_009_vol_adaptive.config import (
    XBI009Config,
    create_default_config,
)
from trading.experiments.xbi_009_vol_adaptive.signal_detector import (
    XBI009SignalDetector,
)


class XBI009Strategy(ExecutionModelStrategy):
    """XBI-009：RSI(2) 均值回歸 + 反轉K線"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI009Config):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(f"  反轉K線: ClosePos >= {config.close_position_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
