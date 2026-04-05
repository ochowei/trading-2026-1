"""
IWM-008: Bollinger Band Squeeze Breakout 優化策略
IWM BB Squeeze Breakout Optimized Strategy

基於 IWM-006 的 BB Squeeze Breakout 架構，三項優化：
1. 持倉延長 20→25 天（讓邊際交易有更多時間達標）
2. 擠壓百分位 25th→30th（擴大有效突破訊號池）
3. 冷卻期 15→10 天（捕捉同波段第二次有效突破）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_008_bb_squeeze_optimized.config import (
    IWM008BBSqueezeConfig,
    create_default_config,
)
from trading.experiments.iwm_008_bb_squeeze_optimized.signal_detector import (
    IWM008BBSqueezeDetector,
)


class IWM008BBSqueezeStrategy(ExecutionModelStrategy):
    """IWM-008：BB Squeeze Breakout 優化策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM008BBSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM008BBSqueezeConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
