"""
USO-021: Bollinger Band Squeeze Breakout 策略
USO BB Squeeze Breakout Strategy

以波動收縮後的向上突破取代均值回歸，捕捉原油趨勢啟動後的爆發性上漲。
USO 追蹤單一商品（原油期貨），不受 ETF 分散化削弱動能的問題。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_021_bb_squeeze_breakout.config import (
    USOBBSqueezeConfig,
    create_default_config,
)
from trading.experiments.uso_021_bb_squeeze_breakout.signal_detector import (
    USOBBSqueezeDetector,
)


class USOBBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """USO-021：BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0010  # 0.10%（USO 高流動性）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USOBBSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USOBBSqueezeConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
