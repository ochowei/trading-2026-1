"""
FXI-002: Volatility-Adaptive Pullback + WR Mean Reversion
(FXI 波動率自適應回檔均值回歸)

使用 Pullback + WR + ATR + ClosePos 過濾訊號架構搭配 ExecutionModelBacktester。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_002_vol_adaptive_pullback.config import (
    FXI002Config,
    create_default_config,
)
from trading.experiments.fxi_002_vol_adaptive_pullback.signal_detector import (
    FXI002SignalDetector,
)


class FXI002Strategy(ExecutionModelStrategy):
    """FXI Volatility-Adaptive Pullback MR (FXI-002)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI002SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI002Config):
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
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
