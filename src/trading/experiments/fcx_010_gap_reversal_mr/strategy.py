"""
FCX-010: Gap-Down 資本化 + 日內反轉均值回歸策略
(FCX Gap-Down Capitulation + Intraday Reversal Mean Reversion)

進場使用隔夜跳空 + 日內反轉 + 回檔 + Williams %R 五重確認，
出場使用固定對稱 TP/SL（TP +5.0%/SL -4.0%）。成交模型採隔日開盤市價。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_010_gap_reversal_mr.config import (
    FCX010Config,
    create_default_config,
)
from trading.experiments.fcx_010_gap_reversal_mr.signal_detector import (
    FCX010SignalDetector,
)


class FCX010Strategy(ExecutionModelStrategy):
    """FCX-010：Gap-Down 資本化 + 日內反轉均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 個股滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX010Config):
            print(f"  隔夜跳空 (Gap): Gap <= {config.gap_threshold:.1%}")
            print("  日內反轉: Close > Open")
            print(f"  日內收盤位置 (ClosePos): >= {config.close_pos_threshold:.0%}")
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
