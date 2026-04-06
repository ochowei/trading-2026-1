"""
SIVR-008: Bollinger Band Squeeze Breakout 策略
SIVR BB Squeeze Breakout Strategy

以波動收縮後的突破取代均值回歸，捕捉白銀價格的趨勢性上漲。
基於 FCX-004 成功經驗移植（FCX 日波動 2-4%，SIVR 日波動 2-3%）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_008_bb_squeeze_breakout.config import (
    SIVRBBSqueezeConfig,
    create_default_config,
)
from trading.experiments.sivr_008_bb_squeeze_breakout.signal_detector import (
    SIVRBBSqueezeDetector,
)


class SIVRBBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """SIVR-008：BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRBBSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRBBSqueezeConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
