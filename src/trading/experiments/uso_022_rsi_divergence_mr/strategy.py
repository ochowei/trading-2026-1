"""
USO RSI(14) Bullish Hook Divergence + USO-013 Mean Reversion Strategy (USO-022)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_022_rsi_divergence_mr.config import (
    USORSIDivergenceMRConfig,
    create_default_config,
)
from trading.experiments.uso_022_rsi_divergence_mr.signal_detector import (
    USORSIDivergenceMRSignalDetector,
)


class USORSIDivergenceMRStrategy(ExecutionModelStrategy):
    """USO-022：RSI(14) bullish hook + USO-013 回檔+RSI(2)+2日急跌均值回歸"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USORSIDivergenceMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USORSIDivergenceMRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%} ~ {abs(config.pullback_max):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  RSI({config.rsi14_period}) Bullish Hook: "
                f"lookback {config.rsi_hook_lookback} 日 / delta ≥ {config.rsi_hook_delta} / "
                f"near-low RSI ≤ {config.rsi_hook_max_min}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
