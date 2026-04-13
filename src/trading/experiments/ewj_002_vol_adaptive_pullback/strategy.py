"""
EWJ-002: Volatility-Adaptive Pullback + WR Mean Reversion

使用 Pullback + WR + ATR 過濾訊號架構搭配 ExecutionModelBacktester。
移除追蹤停損，改用固定 TP/SL 出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewj_002_vol_adaptive_pullback.config import (
    EWJ002Config,
    create_default_config,
)
from trading.experiments.ewj_002_vol_adaptive_pullback.signal_detector import (
    EWJ002SignalDetector,
)


class EWJ002Strategy(ExecutionModelStrategy):
    """EWJ Volatility-Adaptive Pullback MR (EWJ-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWJ002SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWJ002Config):
            print(
                f"  回檔深度: {config.pullback_lookback}日高點回檔"
                f" >= {abs(config.pullback_threshold):.0%}"
                f" (上限 {abs(config.pullback_cap):.0%})"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
