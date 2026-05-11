"""COPX Volume-Confirmed Capitulation MR 策略 (COPX-018)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_018_volume_confirmed_mr.config import (
    COPX018Config,
    create_default_config,
)
from trading.experiments.copx_018_volume_confirmed_mr.signal_detector import (
    COPX018SignalDetector,
)


class COPX018VolumeConfirmedMRStrategy(ExecutionModelStrategy):
    """COPX-018: vol-adaptive MR + volume-surge confirmation gate"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX018SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX018Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            mode = config.volume_filter_mode
            if mode == "ratio_sma":
                print(
                    f"  Volume 過濾 (mode={mode}): "
                    f"Volume / SMA({config.volume_sma_period}) >= "
                    f"{config.volume_ratio_threshold}"
                )
            elif mode == "zscore_60":
                print(
                    f"  Volume 過濾 (mode={mode}): "
                    f"Volume Z-score({config.volume_zscore_period}d) >= "
                    f"{config.volume_zscore_threshold}"
                )
            elif mode == "cum_5d_ratio":
                print(
                    f"  Volume 過濾 (mode={mode}): "
                    f"Cum({config.volume_cum_lookback}d) / Cum_SMA >= "
                    f"{config.volume_cum_threshold}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
