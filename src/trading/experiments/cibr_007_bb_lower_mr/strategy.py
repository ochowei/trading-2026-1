"""
CIBR BB 下軌均值回歸策略 (CIBR BB Lower Band Mean Reversion Strategy)

使用 BB(20,2.0) 下軌觸及作為進場訊號，搭配 WR+ATR+ClosePos 三重品質過濾。
出場使用固定止盈/停損，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_007_bb_lower_mr.config import (
    CIBRBBLowerMRConfig,
    create_default_config,
)
from trading.experiments.cibr_007_bb_lower_mr.signal_detector import (
    CIBRBBLowerMRSignalDetector,
)


class CIBRBBLowerMRStrategy(ExecutionModelStrategy):
    """CIBR-007：BB 下軌均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBRBBLowerMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBRBBLowerMRConfig):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
