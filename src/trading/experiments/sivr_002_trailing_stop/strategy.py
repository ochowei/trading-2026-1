"""
SIVR 追蹤停損均值回歸策略 (SIVR Trailing Stop Mean Reversion Strategy)
進場訊號複用 SIVR-001，出場改用追蹤停損機制。
Signal logic identical to SIVR-001, exit uses trailing stop mechanism.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_003_trailing_stop.trailing_backtester import (
    TrailingStopBacktester,
)
from trading.experiments.sivr_002_trailing_stop.config import (
    SIVRTrailingStopConfig,
    create_default_config,
)
from trading.experiments.sivr_002_trailing_stop.signal_detector import (
    SIVRTrailingStopSignalDetector,
)


class SIVRTrailingStopStrategy(ExecutionModelStrategy):
    """SIVR-002：追蹤停損均值回歸 — 進場不變，追蹤停損出場"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較 GLD 低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRTrailingStopSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> TrailingStopBacktester:
        cfg = create_default_config()
        return TrailingStopBacktester(
            config,
            slippage_pct=self.slippage_pct,
            trail_activation_pct=cfg.trail_activation_pct,
            trail_distance_pct=cfg.trail_distance_pct,
        )

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRTrailingStopConfig):
            print(
                f"  RSI 週期/閾值 (RSI period/thr): "
                f"RSI({config.rsi_period}) < {config.rsi_threshold}"
            )
            print(
                f"  SMA 乖離閾值 (SMA dev thr): "
                f"Close / SMA({config.sma_period}) - 1 <= {config.sma_deviation_threshold:.1%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
            print(f"  追蹤啟動 (Trail activation): +{config.trail_activation_pct:.1%}")
            print(f"  追蹤距離 (Trail distance): {config.trail_distance_pct:.1%}")
        super()._print_strategy_params(config)
