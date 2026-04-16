"""
CIBR 波動率自適應均值回歸策略 (CIBR Volatility-Adaptive Mean Reversion Strategy)

在 CIBR-001 基礎上新增 ATR(5)/ATR(20) 波動率過濾與 ClosePos 日內反轉確認。
出場使用固定止盈/停損（不使用追蹤停損）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_002_vol_adaptive_mr.config import (
    CIBRVolAdaptiveMRConfig,
    create_default_config,
)
from trading.experiments.cibr_002_vol_adaptive_mr.signal_detector import (
    CIBRVolAdaptiveMRSignalDetector,
)


class CIBRVolAdaptiveMRStrategy(ExecutionModelStrategy):
    """CIBR-002：波動率自適應均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBRVolAdaptiveMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBRVolAdaptiveMRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
