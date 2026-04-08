"""
XLU-009: Keltner Channel Squeeze Breakout 策略
XLU Keltner Channel Squeeze Breakout Strategy

使用 TTM Squeeze 概念（BB 收縮至 KC 內部偵測波動壓縮）
+ KC 上軌突破作為進場訊號，捕捉 XLU 公用事業 ETF 波動擴張後的動量上漲。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_009_keltner_squeeze_breakout.config import (
    XLU009KeltnerSqueezeConfig,
    create_default_config,
)
from trading.experiments.xlu_009_keltner_squeeze_breakout.signal_detector import (
    XLU009KeltnerSqueezeDetector,
)


class XLU009KeltnerSqueezeStrategy(ExecutionModelStrategy):
    """XLU-009：Keltner Channel Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU009KeltnerSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU009KeltnerSqueezeConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  KC 參數 (Keltner Channel): EMA({config.kc_ema_period})"
                f" + {config.kc_multiplier}x ATR({config.kc_atr_period})"
            )
            print(f"  Squeeze 條件: BB 在 KC 內部，{config.squeeze_recent_days}日內")
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
