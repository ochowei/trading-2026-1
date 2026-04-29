"""
URA RSI Bullish Divergence + Pullback + WR Mean Reversion Strategy (URA-008)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_008_rsi_divergence_mr.config import (
    URARSIDivergenceMRConfig,
    create_default_config,
)
from trading.experiments.ura_008_rsi_divergence_mr.signal_detector import (
    URARSIDivergenceMRSignalDetector,
)


class URARSIDivergenceMRStrategy(ExecutionModelStrategy):
    """URA-008：RSI(14) bullish hook + URA-002 回檔+WR 均值回歸"""

    slippage_pct: float = 0.0010

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URARSIDivergenceMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URARSIDivergenceMRConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  RSI({config.rsi_period}) Bullish Hook: "
                f"lookback {config.rsi_hook_lookback} 日 / delta ≥ {config.rsi_hook_delta} / "
                f"near-low RSI ≤ {config.rsi_hook_max_min}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
