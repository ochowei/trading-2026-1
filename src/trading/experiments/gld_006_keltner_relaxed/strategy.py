"""
GLD 放寬 Keltner 通道均值回歸策略 (GLD Relaxed Keltner Channel Mean Reversion Strategy)
進場使用 Keltner 下軌 + RSI 放寬閾值，較短冷卻期。
出場沿用追蹤停損。

Entry uses Keltner Channel lower band + relaxed RSI confirmation.
Exit uses trailing stop mechanism.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_003_trailing_stop.trailing_backtester import (
    TrailingStopBacktester,
)
from trading.experiments.gld_006_keltner_relaxed.config import (
    GLDRelaxedKeltnerConfig,
    create_default_config,
)
from trading.experiments.gld_006_keltner_relaxed.signal_detector import (
    GLDRelaxedKeltnerSignalDetector,
)


class GLDRelaxedKeltnerReversionStrategy(ExecutionModelStrategy):
    """GLD 放寬 Keltner 通道均值回歸策略 (GLD-006)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLDRelaxedKeltnerSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> TrailingStopBacktester:
        cfg = create_default_config()
        return TrailingStopBacktester(
            config,
            slippage_pct=self.slippage_pct,
            trail_activation_pct=cfg.trail_activation_pct,
            trail_distance_pct=cfg.trail_distance_pct,
        )

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLDRelaxedKeltnerConfig):
            print(
                f"  RSI 週期/閾值 (RSI period/thr): RSI({config.rsi_period}) < {config.rsi_threshold}"
            )
            print(
                f"  Keltner 通道: EMA({config.ema_period}) ± {config.keltner_multiplier} × ATR({config.atr_period})"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print(f"  追蹤啟動 (Trail activation): +{config.trail_activation_pct:.1%}")
            print(f"  追蹤距離 (Trail distance): {config.trail_distance_pct:.1%}")
        super()._print_strategy_params(config)
