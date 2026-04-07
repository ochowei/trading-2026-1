"""
SIVR-009: Gold/Silver Ratio Mean Reversion 策略
(Gold/Silver Ratio Mean Reversion Strategy)

利用 GLD/SIVR 比率 z-score 均值回歸 + Williams %R 超賣確認。
配對交易/相對價值策略，與 SIVR-001~008 的絕對價格訊號完全不同。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_009_ratio_reversion.config import (
    SIVRRatioReversionConfig,
    create_default_config,
)
from trading.experiments.sivr_009_ratio_reversion.signal_detector import (
    SIVRRatioReversionDetector,
)


class SIVRRatioReversionStrategy(ExecutionModelStrategy):
    """SIVR-009：Gold/Silver Ratio Mean Reversion（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRRatioReversionDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRRatioReversionConfig):
            print(
                f"  比率 z-score (Ratio z-score): GLD/SIVR"
                f" {config.ratio_lookback}日滾動"
                f" >= {config.ratio_zscore_threshold}"
            )
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback}日高點回檔"
                f" {abs(config.pullback_threshold):.1%}"
                f" ~ {abs(config.pullback_cap):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print(f"  參考標的 (Reference): {config.reference_ticker}")
        super()._print_strategy_params(config)
