"""COPX HG=F Direction Filter on Volume-Confirmed MR 策略 (COPX-019)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_019_copper_direction_mr.config import (
    COPX019Config,
    create_default_config,
)
from trading.experiments.copx_019_copper_direction_mr.signal_detector import (
    COPX019SignalDetector,
)


class COPX019CopperDirectionMRStrategy(ExecutionModelStrategy):
    """COPX-019: vol-adaptive MR + volume-surge + HG=F copper direction regime gate"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX019SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX019Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            print(
                f"  Volume Z-score({config.volume_zscore_period}d) >= "
                f"{config.volume_zscore_threshold}"
            )
            mode = config.copper_filter_mode
            if mode == "return_floor":
                print(
                    f"  HG=F direction (mode={mode}): "
                    f"{config.copper_lookback}d return >= "
                    f"{config.min_copper_return:.2%}"
                )
            elif mode == "return_ceil":
                print(
                    f"  HG=F direction (mode={mode}): "
                    f"{config.copper_lookback}d return <= "
                    f"{config.max_copper_return:.2%}"
                )
            elif mode == "level_floor":
                print(
                    f"  HG=F level (mode={mode}): "
                    f"Close / SMA({config.copper_sma_period}) >= "
                    f"{config.copper_level_floor:.2f}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
