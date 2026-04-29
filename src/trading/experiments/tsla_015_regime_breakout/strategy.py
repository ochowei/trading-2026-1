"""
TSLA-015: Multi-Week Regime-Aware BB Squeeze Breakout 策略

直接回應 TSLA-013 提出的「regime-level filters may be required for high-vol stocks」
跨資產假設，將多週期趨勢與波動 regime 過濾疊加於 TSLA-009 Att2 BB Squeeze 突破之上。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_015_regime_breakout.config import (
    TSLA015Config,
    create_default_config,
)
from trading.experiments.tsla_015_regime_breakout.signal_detector import (
    TSLA015RegimeBreakoutDetector,
)


class TSLA015RegimeBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-015: 多週期 regime 過濾 BB Squeeze Breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA015RegimeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA015Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" ≥ {config.sma_regime_ratio_min}"
                f" × SMA({config.sma_regime_long})"
            )
            if config.use_vol_regime:
                print(
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用 (Att3 ablation)")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
