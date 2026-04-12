"""
EEM-005: BB Squeeze Breakout
(EEM 布林帶擠壓突破)

TSLA-009 驗證有效的 BB Squeeze 框架移植至 EEM，測試突破策略在分散化 ETF 上的效果。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_005_bb_squeeze_breakout.config import (
    EEM005Config,
    create_default_config,
)
from trading.experiments.eem_005_bb_squeeze_breakout.signal_detector import (
    EEM005SignalDetector,
)


class EEM005Strategy(ExecutionModelStrategy):
    """EEM BB 擠壓突破 (EEM-005)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM005Config):
            print(f"  布林帶 (BB): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓偵測: {config.bb_squeeze_percentile_window} 日"
                f" {config.bb_squeeze_percentile:.0%} 百分位,"
                f" 近 {config.bb_squeeze_recent_days} 日"
            )
            print(f"  趨勢確認: SMA({config.sma_trend_period})")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
