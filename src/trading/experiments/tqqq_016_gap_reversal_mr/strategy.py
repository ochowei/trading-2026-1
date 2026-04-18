"""
TQQQ-016: Gap-Down 資本化 + 日內反轉均值回歸策略
(TQQQ Gap-Down Capitulation + Intraday Reversal Mean Reversion)

進場使用 20日回撤 + RSI(5) + 隔夜跳空 + 日內反轉 + Volume 五重確認（Att3 最終版），
出場使用固定 TP/SL（TP +7%/SL -8%/10天，同 TQQQ-010）。
成交模型採隔日開盤市價 + 0.1% 滑價 + 悲觀認定。
三次迭代全部失敗（min(A,B) -0.07 vs TQQQ-010 的 0.36），詳見 config.py 迭代歷程。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_016_gap_reversal_mr.config import (
    TQQQ016Config,
    create_default_config,
)
from trading.experiments.tqqq_016_gap_reversal_mr.signal_detector import (
    TQQQ016SignalDetector,
)


class TQQQ016Strategy(ExecutionModelStrategy):
    """TQQQ-016：Gap-Down 資本化 + 日內反轉均值回歸"""

    slippage_pct: float = 0.001  # 0.1%

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQ016Config):
            print(
                f"  回撤 (Drawdown): {config.drawdown_lookback}日高點回撤"
                f" <= {config.drawdown_threshold:.0%}"
            )
            print(f"  RSI: RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  隔夜跳空 (Gap): Gap <= {config.gap_threshold:.1%}")
            print("  日內反轉: Close > Open")
            print(
                f"  成交量 (Volume): Volume > {config.volume_multiplier}x"
                f" SMA({config.volume_sma_period})"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
