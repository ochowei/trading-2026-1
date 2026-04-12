"""
EEM-006: RS Momentum Pullback 策略
EEM Relative Strength Momentum Pullback Strategy

利用 EEM 相對 SPY 的超額表現（EM > DM），
在短期回調時買入，捕捉 EM 資金流動量。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_006_rs_momentum_pullback.config import (
    EEMRSMomentumConfig,
    create_default_config,
)
from trading.experiments.eem_006_rs_momentum_pullback.signal_detector import (
    EEMRSMomentumDetector,
)


class EEMRSMomentumStrategy(ExecutionModelStrategy):
    """EEM-006：RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEMRSMomentumDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEMRSMomentumConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): EEM - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
