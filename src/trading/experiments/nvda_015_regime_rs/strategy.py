"""
NVDA-015: Multi-Week Regime-Aware Relative Strength Momentum Pullback 策略

跨**策略類型**首次將 lesson #22 buffered multi-week SMA regime gate +
ATR vol regime（NVDA-013 Att3 雙重 gate）應用於 RS Momentum Pullback
框架（先前皆於 BB Squeeze、MBPC、Pullback MR 三類框架）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_015_regime_rs.config import (
    NVDA015Config,
    create_default_config,
)
from trading.experiments.nvda_015_regime_rs.signal_detector import (
    NVDA015RegimeRSDetector,
)


class NVDA015RegimeRSStrategy(ExecutionModelStrategy):
    """NVDA-015：Multi-Week Regime-Aware RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA015RegimeRSDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA015Config):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): NVDA - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" >= {config.sma_regime_ratio_min}"
                f" x SMA({config.sma_regime_long})"
            )
            if config.use_vol_regime:
                print(
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" <= {config.vol_regime_max_ratio}"
                    f" x ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
