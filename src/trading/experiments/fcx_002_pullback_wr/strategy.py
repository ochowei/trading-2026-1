"""
FCX 回檔 + Williams %R + 反轉K線均值回歸策略
FCX Pullback + Williams %R + Reversal Candle Mean Reversion Strategy

串接配置 -> 訊號偵測器 -> 成交模型回測引擎。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_002_pullback_wr.config import (
    FCXPullbackWRConfig,
    create_default_config,
)
from trading.experiments.fcx_002_pullback_wr.signal_detector import (
    FCXPullbackWRDetector,
)


class FCXPullbackWRStrategy(ExecutionModelStrategy):
    """FCX 回檔 + Williams %R + 反轉K線均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% 個股滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCXPullbackWRDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCXPullbackWRConfig):
            print(
                f"  回檔閾值 (Pullback thr): {config.pullback_lookback}日高點跌幅 <= {config.pullback_threshold:.0%}"
            )
            print(f"  Williams %%R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  反轉K線 (Close pos): >= {config.close_position_threshold:.0%}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
