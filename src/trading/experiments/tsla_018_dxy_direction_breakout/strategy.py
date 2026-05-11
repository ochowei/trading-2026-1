"""
TSLA-018: DXY 5d Direction Filter on TSLA-QQQ Cross-Asset Divergence BB Squeeze Breakout

直接回應 TSLA AI_CONTEXT「TSLA Sharpe 0.96 上限突破方向」之新跨資產維度試驗：
DXY (US Dollar Index) 5d direction filter 為 lesson #24 family v7 spot FX direction
變體（GLD-016 Att1 / COPX-016 Att3 已驗證），repo 首次應用於高波動 AI 個股 +
BB Squeeze Breakout 框架。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_018_dxy_direction_breakout.config import (
    TSLA018Config,
    create_default_config,
)
from trading.experiments.tsla_018_dxy_direction_breakout.signal_detector import (
    TSLA018DXYDirectionBreakoutDetector,
)


class TSLA018DXYDirectionBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-018: TSLA-017 Att3 框架 + DXY 5d direction filter（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA018DXYDirectionBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA018Config):
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
            print(
                f"  DXY direction filter: DXY {config.dxy_lookback}d 變化"
                f" ≤ {config.max_dxy_change:+.2%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
