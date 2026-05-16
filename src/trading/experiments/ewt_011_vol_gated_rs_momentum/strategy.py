"""EWT Volatility-Regime-Gated RS Momentum Pullback 策略 (EWT-011)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_011_vol_gated_rs_momentum.config import (
    EWT011Config,
    create_default_config,
)
from trading.experiments.ewt_011_vol_gated_rs_momentum.signal_detector import (
    EWT011SignalDetector,
)


class EWT011Strategy(ExecutionModelStrategy):
    """EWT-011：EWT-007 RS 動量回調 + 波動率 regime 閘門（執行模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT011Config):
            print(
                f"  RS: EWT − {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(f"  5日高點回撤 ∈ [{config.pullback_min:.0%}, {config.pullback_max:.0%}]")
            print(f"  Close > SMA({config.sma_trend_period})")
            if config.use_vol_regime_gate:
                print(
                    f"  波動率 regime 閘門: ATR({config.atr_period})/Close"
                    f" <= {config.max_atr_pct:.1%}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
