"""
IBIT-002: 回檔 + Williams %R 均值回歸（出場優化）
(IBIT Pullback + WR Mean Reversion with Exit Optimization)

同 IBIT-001 進場，測試 SL -6.0%（收窄自 -7.0%）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ibit_002_rsi2_pullback.config import (
    IBITRSI2PullbackConfig,
    create_default_config,
)
from trading.experiments.ibit_002_rsi2_pullback.signal_detector import (
    IBITRSI2PullbackSignalDetector,
)


class IBITRSI2PullbackStrategy(ExecutionModelStrategy):
    """IBIT-002：回檔 + WR 均值回歸（出場優化）"""

    slippage_pct: float = 0.0015  # 0.15% 加密貨幣 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IBITRSI2PullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IBITRSI2PullbackConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
