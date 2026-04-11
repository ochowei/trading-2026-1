"""
IBIT-005: 均值回歸 SL -8% 出場優化策略
(IBIT Mean Reversion SL -8% Exit Optimization Strategy)

同 IBIT-001 進場，僅調整停損至 -8%（測試 -7% 與 -9% 之間的未探索值）。
不使用追蹤停損（日波動 ~3.17%，禁用區域）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ibit_005_extended_lookback.config import (
    IBIT005Config,
    create_default_config,
)
from trading.experiments.ibit_005_extended_lookback.signal_detector import (
    IBIT005SignalDetector,
)


class IBIT005Strategy(ExecutionModelStrategy):
    """IBIT-005：均值回歸 SL -8%"""

    slippage_pct: float = 0.0015  # 0.15% 加密貨幣 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IBIT005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IBIT005Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
