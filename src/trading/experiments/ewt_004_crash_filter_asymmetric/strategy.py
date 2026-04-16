"""
EWT-004: 2-Day Crash Filter + Asymmetric Exit Mean Reversion
(EWT 2日急跌過濾 + 非對稱出場均值回歸)

在 EWT-002 的 pullback+WR+ATR 基礎上加入 2 日急跌過濾，
並調整為非對稱出場（TP +5.0% / SL -4.5%）提高盈虧比。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_004_crash_filter_asymmetric.config import (
    EWT004Config,
    create_default_config,
)
from trading.experiments.ewt_004_crash_filter_asymmetric.signal_detector import (
    EWT004SignalDetector,
)


class EWT004Strategy(ExecutionModelStrategy):
    """EWT 2-Day Crash Filter + Asymmetric Exit MR (EWT-004)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT004Config):
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
