"""
EWZ-004: Short-Window WR Mean Reversion
(EWZ 短窗口 WR 均值回歸)

使用 Pullback + WR(5) + ClosePos 過濾訊號架構搭配 ExecutionModelBacktester。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewz_004_trend_momentum_pullback.config import (
    EWZ004Config,
    create_default_config,
)
from trading.experiments.ewz_004_trend_momentum_pullback.signal_detector import (
    EWZ004SignalDetector,
)


class EWZ004Strategy(ExecutionModelStrategy):
    """EWZ Short-Window WR Mean Reversion (EWZ-004)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWZ004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWZ004Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback}日高點回檔"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", 上限 <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
