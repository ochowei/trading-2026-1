"""
SPY-008: Bollinger Band Squeeze Breakout 策略
SPY BB Squeeze Breakout Strategy

以波動收縮後的突破捕捉 SPY 動能行情。
基於 TSLA-005/NVDA-004/FCX-004 成功經驗移植至低波動大盤指數。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.spy_008_bb_squeeze_breakout.config import (
    SPYBBSqueezeConfig,
    create_default_config,
)
from trading.experiments.spy_008_bb_squeeze_breakout.signal_detector import (
    SPYBBSqueezeDetector,
)


class SPYBBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """SPY-008：BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPYBBSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPYBBSqueezeConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
