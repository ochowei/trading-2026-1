"""
COPX-002: 回檔 10-18% + Williams %R 均值回歸策略
(COPX Pullback 10-18% + WR Mean Reversion Strategy)

基於 COPX-001 架構，收緊回檔下限至 10% 以移除低品質淺回檔訊號。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_002_deep_drawdown.config import (
    COPX002Config,
    create_default_config,
)
from trading.experiments.copx_002_deep_drawdown.signal_detector import (
    COPX002Detector,
)


class COPXDeepDrawdownStrategy(ExecutionModelStrategy):
    """COPX-002：回檔 10-18% + WR 均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX002Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX002Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
