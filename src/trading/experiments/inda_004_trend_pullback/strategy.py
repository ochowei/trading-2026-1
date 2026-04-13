"""
INDA-004: Trend Pullback (趨勢回調買入)

Buy pullbacks in INDA's uptrend. Uses SMA(50) trend filter + WR(10) oversold.
Execution model: next_open_market, 0.1% slippage.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_004_trend_pullback.config import (
    INDATrendPullbackConfig,
    create_default_config,
)
from trading.experiments.inda_004_trend_pullback.signal_detector import (
    INDATrendPullbackDetector,
)


class INDATrendPullbackStrategy(ExecutionModelStrategy):
    """INDA 趨勢回調策略 (INDA-004)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDATrendPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDATrendPullbackConfig):
            print(
                f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})"
                f" + slope > 0 ({config.sma_slope_lookback}d)"
            )
            print(
                f"  回調門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回調上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
