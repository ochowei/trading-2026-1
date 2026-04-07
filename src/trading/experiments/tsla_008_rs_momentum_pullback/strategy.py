"""
TSLA-008: BB Squeeze Breakout + Golden Cross 策略
TSLA BB Squeeze with SMA Golden Cross Strategy

以 TSLA-005 的 BB Squeeze 為基礎，用 SMA(20)>SMA(50) 金叉
取代 Close>SMA(50) 作為趨勢確認，嘗試過濾熊市假突破。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_008_rs_momentum_pullback.config import (
    TSLA008Config,
    create_default_config,
)
from trading.experiments.tsla_008_rs_momentum_pullback.signal_detector import (
    TSLA008Detector,
)


class TSLARSMomentumPullbackStrategy(ExecutionModelStrategy):
    """TSLA-008：BB Squeeze + Golden Cross（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA008Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA008Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(
                f"  趨勢確認 (Trend): SMA({config.sma_short_period})"
                f" > SMA({config.sma_long_period}) Golden Cross"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
