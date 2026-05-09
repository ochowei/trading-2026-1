"""TSLA-019: ^VIX BANDS Regime Gate on TSLA-017 Att3 BB Squeeze Breakout 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_019_vix_bands_breakout.config import (
    TSLA019Config,
    create_default_config,
)
from trading.experiments.tsla_019_vix_bands_breakout.signal_detector import (
    TSLA019VixBandsBreakoutDetector,
)


class TSLA019VixBandsBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-019: ^VIX BANDS regime gate on TSLA-017 Att3 framework"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA019VixBandsBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA019Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" >= {config.sma_regime_ratio_min}"
                f" x SMA({config.sma_regime_long})"
            )
            print(
                f"  跨資產背離 regime: TSLA - {config.benchmark_ticker}"
                f" {config.divergence_lookback}d 報酬差 >= {config.min_relative_return:+.2%}"
            )
            print(
                f"  VIX BANDS: VIX <= {config.vix_low_threshold:.1f}"
                f" OR VIX > {config.vix_high_threshold:.1f}（排除中段）"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
