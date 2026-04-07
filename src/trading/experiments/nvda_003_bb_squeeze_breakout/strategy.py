"""
NVDA-003: Bollinger Band Squeeze Breakout 策略
NVDA BB Squeeze Breakout Strategy

以波動收縮後的突破取代均值回歸，捕捉 NVDA 動量驅動的爆發性上漲。
基於 TSLA-005 成功經驗移植。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_003_bb_squeeze_breakout.config import (
    NVDABBSqueezeConfig,
    create_default_config,
)
from trading.experiments.nvda_003_bb_squeeze_breakout.signal_detector import (
    NVDABBSqueezeDetector,
)


class NVDABBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """NVDA-003：BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDABBSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDABBSqueezeConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
