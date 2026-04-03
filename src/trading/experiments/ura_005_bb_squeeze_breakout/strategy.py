"""
URA-005: BB Squeeze Breakout 策略
URA BB Squeeze Breakout Strategy

URA 首次嘗試突破策略。基於 NVDA-004 / FCX-004 模板，
按 URA 波動度 (2.34%) 縮放參數。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_005_bb_squeeze_breakout.config import (
    URABBSqueezeBreakoutConfig,
    create_default_config,
)
from trading.experiments.ura_005_bb_squeeze_breakout.signal_detector import (
    URABBSqueezeBreakoutDetector,
)


class URABBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """URA-005: BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URABBSqueezeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URABBSqueezeBreakoutConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
