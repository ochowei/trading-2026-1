"""
EWT-006: Optimized Exit Mean Reversion
(EWT 出場優化均值回歸)

基於 EWT-004 的 pullback+WR+ATR+2日急跌入場框架，
優化出場參數（TP +3.5% / SL -4.5% / 15d）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_006_optimized_exit_mr.config import (
    EWT006Config,
    create_default_config,
)
from trading.experiments.ewt_006_optimized_exit_mr.signal_detector import (
    EWT006SignalDetector,
)


class EWT006Strategy(ExecutionModelStrategy):
    """EWT Optimized Exit Mean Reversion (EWT-006)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT006SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT006Config):
            print(
                f"  回檔深度: {config.pullback_lookback}日高點回檔"
                f" >= {abs(config.pullback_threshold):.0%}"
            )
            print(f"  回檔上限: <= {abs(config.pullback_cap):.0%}（隔離極端崩盤）")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2日急跌: 2日報酬 <= {config.drop_2d_threshold:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
