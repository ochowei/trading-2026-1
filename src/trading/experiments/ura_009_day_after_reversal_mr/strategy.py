"""URA Day-After Capitulation Mean Reversion Strategy (URA-009)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_009_day_after_reversal_mr.config import (
    URADayAfterReversalMRConfig,
    create_default_config,
)
from trading.experiments.ura_009_day_after_reversal_mr.signal_detector import (
    URADayAfterReversalMRSignalDetector,
)


class URADayAfterReversalMRStrategy(ExecutionModelStrategy):
    """URA-009：日後資本化 + 單K反轉 均值回歸"""

    slippage_pct: float = 0.0010

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URADayAfterReversalMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URADayAfterReversalMRConfig):
            print(
                f"  昨日回檔 (Prev Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  昨日 WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(f"  兩日跌幅 (T-3→T-1): ≤ {config.two_day_decline:.0%}")
            print("  今日反轉強度: Close > 昨日 High 且 Close > 今日 Open")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
