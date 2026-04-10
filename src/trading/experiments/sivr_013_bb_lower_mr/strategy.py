"""
SIVR-013: Bollinger Band 下軌均值回歸策略
(SIVR BB Lower Band Mean Reversion Strategy)

以 BB(20,2) 下軌取代固定回檔門檻，提供波動度自適應的進場機制。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_013_bb_lower_mr.config import (
    SIVR013Config,
    create_default_config,
)
from trading.experiments.sivr_013_bb_lower_mr.signal_detector import (
    SIVR013SignalDetector,
)


class SIVR013Strategy(ExecutionModelStrategy):
    """SIVR-013：BB 下軌均值回歸"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVR013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVR013Config):
            print(f"  Bollinger Band: BB({config.bb_period}, {config.bb_std}) Close < Lower Band")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            print(
                f"  回檔上限: {config.pullback_lookback} 日高點回檔"
                f" <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
