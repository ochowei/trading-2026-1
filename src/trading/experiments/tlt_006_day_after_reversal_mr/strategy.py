"""TLT Day-After Capitulation + 強反轉 K 線均值回歸策略 (TLT-006)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_006_day_after_reversal_mr.config import (
    TLT006Config,
    create_default_config,
)
from trading.experiments.tlt_006_day_after_reversal_mr.signal_detector import (
    TLT006SignalDetector,
)


class TLTDayAfterReversalMRStrategy(ExecutionModelStrategy):
    """TLT-006：日後資本化 + 單K反轉"""

    slippage_pct: float = 0.001  # 0.1%（TLT 為高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT006SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT006Config):
            print(
                f"  昨日回檔 (Prev Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  昨日 WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(f"  兩日跌幅 (T-3→T-1): ≤ {config.two_day_decline:.1%}")
            print("  今日反轉強度: Close > 昨日 High 且 Close > 今日 Open")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
