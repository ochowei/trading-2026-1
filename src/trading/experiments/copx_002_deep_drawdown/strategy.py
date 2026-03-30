"""
COPX-002: 20日回檔 + Williams %R + 延長持倉 均值回歸策略
(COPX 20-Day Pullback + Williams %R + Extended Holding Strategy)

相比 COPX-001：使用 20 日回看窗口（vs 10 日）確認更深的回檔，
搭配 20 天持倉（vs 15 天）給予更充裕的反彈時間。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_002_deep_drawdown.config import (
    COPXDeepDrawdownConfig,
    create_default_config,
)
from trading.experiments.copx_002_deep_drawdown.signal_detector import (
    COPXDeepDrawdownSignalDetector,
)


class COPXDeepDrawdownStrategy(ExecutionModelStrategy):
    """COPX-002：20日回檔 + Williams %R + 延長持倉"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPXDeepDrawdownSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPXDeepDrawdownConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
