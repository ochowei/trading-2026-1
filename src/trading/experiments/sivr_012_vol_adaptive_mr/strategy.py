"""
SIVR-012: Volatility-Adaptive Mean Reversion
(SIVR 波動率自適應均值回歸)

SIVR-005 framework + ATR(5)/ATR(20) > 1.15 filter to distinguish
sharp panic pullbacks from gradual declines.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_012_vol_adaptive_mr.config import (
    SIVRVolAdaptiveMRConfig,
    create_default_config,
)
from trading.experiments.sivr_012_vol_adaptive_mr.signal_detector import (
    SIVRVolAdaptiveMRDetector,
)


class SIVRVolAdaptiveMRStrategy(ExecutionModelStrategy):
    """SIVR 波動率自適應均值回歸 (SIVR-012)"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較 GLD 低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRVolAdaptiveMRDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRVolAdaptiveMRConfig):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
