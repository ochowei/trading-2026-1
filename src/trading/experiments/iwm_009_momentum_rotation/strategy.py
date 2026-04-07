"""
IWM-009: Small-Cap Momentum Pullback (IWM/SPY)

當 IWM 相對 SPY 表現強勢（正向輪動中）且短期回檔時買入。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_009_momentum_rotation.config import (
    IWM009Config,
    create_default_config,
)
from trading.experiments.iwm_009_momentum_rotation.signal_detector import (
    IWM009SignalDetector,
)


class IWM009Strategy(ExecutionModelStrategy):
    """IWM-009：Small-Cap Momentum Pullback IWM/SPY（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM009Config):
            print(f"  配對標的 (Pair): IWM vs {config.pair_ticker}")
            print(
                f"  相對強勢 (RS): IWM {config.relative_return_lookback}d ret"
                f" - SPY >= {config.relative_outperform_threshold:.1%}"
            )
            print(
                f"  短期回檔 (Pullback): {config.pullback_days}d ret"
                f" <= {config.pullback_threshold:.1%}"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} ��易日")
        super()._print_strategy_params(config)
