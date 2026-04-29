"""
USO-023: 波動率自適應均值回歸策略 (USO Volatility-Adaptive Mean Reversion)

USO-013 框架 + ATR(5)/ATR(20) 波動率飆升過濾，目標改善 USO-013 Part A 結構性
弱勢（0.26 vs Part B 0.82）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_023_vol_adaptive_mr.config import (
    USO023Config,
    create_default_config,
)
from trading.experiments.uso_023_vol_adaptive_mr.signal_detector import (
    USO023SignalDetector,
)


class USO023Strategy(ExecutionModelStrategy):
    """USO-023：波動率自適應均值回歸"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USO023SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USO023Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%} ~ {abs(config.pullback_max):.1%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  2日報酬 (2-Day Drop) 範圍: "
                f"{config.drop_2d_cap:.1%} <= Return_2d <= {config.drop_2d_threshold:.1%}"
            )
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
