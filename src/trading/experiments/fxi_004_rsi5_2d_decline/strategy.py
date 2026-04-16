"""
FXI-004: 2-Day Decline Mean Reversion
(FXI 2日急跌均值回歸)

使用 Pullback + WR(10) + 2日急跌過濾訊號架構搭配 ExecutionModelBacktester。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_004_rsi5_2d_decline.config import (
    FXI004Config,
    create_default_config,
)
from trading.experiments.fxi_004_rsi5_2d_decline.signal_detector import (
    FXI004SignalDetector,
)


class FXI004Strategy(ExecutionModelStrategy):
    """FXI 2-Day Decline MR (FXI-004)"""

    slippage_pct: float = 0.001  # 0.1%

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI004Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback}日高點回檔"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", 上限 <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  2日急跌 (2-Day Decline): <= {config.decline_2d_threshold:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
