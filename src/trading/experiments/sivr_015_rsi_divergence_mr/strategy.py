"""
SIVR RSI Bullish Divergence + Pullback+WR Mean Reversion Strategy (SIVR-015)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_015_rsi_divergence_mr.config import (
    SIVRRSIDivergenceMRConfig,
    create_default_config,
)
from trading.experiments.sivr_015_rsi_divergence_mr.signal_detector import (
    SIVRRSIDivergenceMRSignalDetector,
)


class SIVRRSIDivergenceMRStrategy(ExecutionModelStrategy):
    """SIVR-015：RSI bullish hook + SIVR-005 回檔+WR 均值回歸"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRRSIDivergenceMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRRSIDivergenceMRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%}"
                f" ~ {abs(config.pullback_cap):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  RSI({config.rsi_period}) Bullish Hook: "
                f"lookback {config.rsi_hook_lookback} 日 / delta ≥ {config.rsi_hook_delta} / "
                f"near-low RSI ≤ {config.rsi_hook_max_min}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
