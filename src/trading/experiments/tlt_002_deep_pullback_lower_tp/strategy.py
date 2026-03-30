"""
TLT 回檔 + WR + 反轉K線 + 中期跌幅過濾均值回歸策略
(TLT Pullback + WR + Reversal + Medium-term Drawdown Filter Strategy)

改進自 TLT-001：加入 60 日跌幅 <= 10% 過濾器，
區分「正常環境回檔」與「持續性熊市回檔」。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_002_deep_pullback_lower_tp.config import (
    TLTDeepPullbackLowerTPConfig,
    create_default_config,
)
from trading.experiments.tlt_002_deep_pullback_lower_tp.signal_detector import (
    TLTDeepPullbackLowerTPSignalDetector,
)


class TLTDeepPullbackLowerTPStrategy(ExecutionModelStrategy):
    """TLT 回檔 + WR + 反轉K線 + 中期跌幅過濾均值回歸策略 (TLT-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLTDeepPullbackLowerTPSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLTDeepPullbackLowerTPConfig):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  中期跌幅過濾 (MT DD filter): {config.medium_term_lookback} 日跌幅"
                f" <= {abs(config.medium_term_max_drawdown):.0%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
