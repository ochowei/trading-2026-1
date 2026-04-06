"""
IBIT-003: RSI(5) Trend Pullback 策略 (Attempt 3)
IBIT RSI(5) Trend Pullback Strategy

RSI(5) 在高波動 ETF 有效（SOXL 驗證），搭配 SMA(20) 短期趨勢確認。
TP +5% 匹配 IBIT-001 已驗證的 TP 上限。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ibit_003_bb_squeeze_breakout.config import (
    IBITRsi5TrendConfig,
    create_default_config,
)
from trading.experiments.ibit_003_bb_squeeze_breakout.signal_detector import (
    IBITBBSqueezeDetector,
)


class IBITBBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """IBIT-003：RSI(5) Trend Pullback 策略（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% 加密貨幣 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IBITBBSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IBITRsi5TrendConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  RSI: RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
