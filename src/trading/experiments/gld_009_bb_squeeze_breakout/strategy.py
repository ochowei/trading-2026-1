"""
GLD-009: BB Squeeze Breakout 策略
GLD BB Squeeze Breakout Strategy

首次在 GLD 上嘗試突破策略。GLD 是單一商品 ETF（金條），
突破動能不會被分散化稀釋。

最佳版本為 Att1（固定 TP/SL，無追蹤停損）。
Att2（SL -3.5%）和 Att3（追蹤停損）均劣化。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_009_bb_squeeze_breakout.config import (
    GLD009Config,
    create_default_config,
)
from trading.experiments.gld_009_bb_squeeze_breakout.signal_detector import (
    GLD009SignalDetector,
)


class GLDBBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """GLD-009：BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD009Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
