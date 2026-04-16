"""
EWT-002: Volatility-Adaptive Pullback + WR Mean Reversion
(EWT 波動率自適應回檔均值回歸)

移除 EWT-001 的追蹤停損（啟動/TP 比 55.6% < 80% 壓縮獲利），
改用固定 TP/SL + ATR 波動率飆升過濾 + 回檔上限隔離極端崩盤。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_002_vol_adaptive_pullback.config import (
    EWT002Config,
    create_default_config,
)
from trading.experiments.ewt_002_vol_adaptive_pullback.signal_detector import (
    EWT002SignalDetector,
)


class EWT002Strategy(ExecutionModelStrategy):
    """EWT Volatility-Adaptive Pullback MR (EWT-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT002SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT002Config):
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
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
