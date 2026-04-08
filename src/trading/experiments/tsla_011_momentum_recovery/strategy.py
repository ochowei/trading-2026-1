"""
TSLA-011: Breakout from Oversold Base Strategy

Buy when TSLA makes a new 20-day high after having been in deep pullback (-20%+).
This is a breakout/momentum strategy, fundamentally different from mean reversion:
- Mean reversion: buy at the oversold extreme
- Breakout: buy when the stock confirms recovery by breaking above recent resistance
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_011_momentum_recovery.config import (
    TSLABreakoutConfig,
    create_default_config,
)
from trading.experiments.tsla_011_momentum_recovery.signal_detector import (
    TSLABreakoutDetector,
)


class TSLAMomentumRecoveryStrategy(ExecutionModelStrategy):
    """TSLA-011：回檔後突破策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLABreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLABreakoutConfig):
            print(f"  回撤回看 (Drawdown lookback): {config.drawdown_lookback} 日")
            print(f"  回檔檢查窗口 (Pullback lookback): {config.pullback_lookback} 日")
            print(f"  回檔深度門檻 (Pullback threshold): {config.pullback_threshold:.0%}")
            print(f"  突破回看 (Breakout lookback): {config.breakout_lookback} 日")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
