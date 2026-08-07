"""NVDA-016: sector-health confirmed MBPC strategy."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_016_sector_confirmed_mbpc.config import (
    NVDA016Config,
    create_default_config,
)
from trading.experiments.nvda_016_sector_confirmed_mbpc.signal_detector import (
    NVDA016SectorConfirmedMBPCDetector,
)


class NVDA016SectorConfirmedMBPCStrategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """NVDA sector-health confirmed MBPC with a verified SMH bundle."""

    bundle_trial_family = "NVDA:sector-confirmed-mbpc"
    bundle_trial_hypothesis = (
        "NVDA breakout pullbacks improve when semiconductor-sector momentum confirms the move."
    )
    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA016SectorConfirmedMBPCDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA016Config):
            print(
                f"  Donchian: {config.donchian_period} 日新高，近 "
                f"{config.breakout_recency_days} 日內 breakout"
            )
            print(f"  趨勢確認: Close > SMA({config.sma_trend_period})")
            print(
                f"  板塊健康閘門: {config.macro_ticker} "
                f"{config.macro_lookback}d >= {config.macro_min_return:.1%}"
            )
            print(f"  冷卻期: {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
