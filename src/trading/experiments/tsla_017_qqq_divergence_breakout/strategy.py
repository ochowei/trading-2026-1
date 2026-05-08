"""
TSLA-017: TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout 策略

直接回應 TSLA AI_CONTEXT 提出的「TSLA 結構性 Sharpe 0.53 上限仍待跨維度突破」
（^VXN forward-looking implied vol、TSLA-QQQ cross-asset divergence、^VIX BANDS）。
本實驗為 repo 首次將 TLT-014 cross-asset divergence regime gate 移植至高波動 AI
個股 BB Squeeze breakout 框架。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_017_qqq_divergence_breakout.config import (
    TSLA017Config,
    create_default_config,
)
from trading.experiments.tsla_017_qqq_divergence_breakout.signal_detector import (
    TSLA017QQQDivergenceBreakoutDetector,
)


class TSLA017QQQDivergenceBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-017: TSLA-QQQ 跨資產背離 regime gate + BB Squeeze breakout（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA017QQQDivergenceBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA017Config):
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
            print(
                f"  跨資產背離 regime: TSLA - {config.benchmark_ticker}"
                f" {config.divergence_lookback}d 報酬差 ≥ {config.min_relative_return:+.2%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
