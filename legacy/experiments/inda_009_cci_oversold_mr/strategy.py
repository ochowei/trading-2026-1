"""
INDA-009: CCI Oversold Reversal Mean Reversion
(INDA CCI 深度超賣 + 反轉均值回歸)

Uses execution model with fixed TP/SL exit.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import PrimaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_009_cci_oversold_mr.config import (
    INDA009Config,
    create_default_config,
)
from trading.experiments.inda_009_cci_oversold_mr.signal_detector import (
    INDA009SignalDetector,
)


class INDA009Strategy(PrimaryBundleStrategyMixin, ExecutionModelStrategy):
    """INDA CCI 超賣反轉均值回歸 (INDA-009)"""

    bundle_trial_family = "INDA:cci-oversold-mr"
    bundle_trial_hypothesis = (
        "INDA CCI oversold mean reversion can be reproduced from a verified primary bundle."
    )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA009Config):
            print(f"  CCI 週期: {config.cci_period}")
            print(f"  CCI 超賣門檻: <= {config.cci_oversold:.1f}")
            print(
                f"  CCI 轉折: 今日 CCI - 過去 {config.cci_turn_lookback} 日 CCI 最低點"
                f" >= {config.cci_turn_delta:.1f}"
            )
            print(f"  反轉 K 線 (Close > Open): {'是' if config.require_close_gt_open else '否'}")
            if config.use_close_pos:
                print(f"  收盤位置過濾: >= {config.close_pos_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
