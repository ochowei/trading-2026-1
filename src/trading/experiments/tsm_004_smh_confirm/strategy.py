"""
TSM 回檔上限策略
TSM Capped Pullback Strategy

基於 TSM-002 架構，加入回檔上限以過濾極端崩盤訊號。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_004_smh_confirm.config import (
    TSMSMHConfirmConfig,
    create_default_config,
)
from trading.experiments.tsm_004_smh_confirm.signal_detector import (
    TSMSMHConfirmDetector,
)


class TSMSMHConfirmStrategy(ExecutionModelStrategy):
    """TSM 回檔上限策略 (TSM-004)"""

    slippage_pct: float = 0.0010  # 0.10% 大型 ADR 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMSMHConfirmDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMSMHConfirmConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%} ~ "
                f"{abs(config.pullback_upper_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
