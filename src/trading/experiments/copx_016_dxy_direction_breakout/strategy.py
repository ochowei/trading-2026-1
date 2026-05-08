"""
COPX-016: DXY Direction Filter on Multi-Week Regime-Aware BB Squeeze Breakout

在 COPX-011 Att3 框架（regime BOX [k_min=1.00, k_max=1.09]，min(A,B) 0.64）
之上疊加「DXY 5 日報酬 ≤ +0.5%」過濾。

預期成果（Att1）：
- 過濾 2019-04-01 唯一 Part A SL（DXY 5d +0.70%）
- 保留全部 7 Part A TPs（DXY 5d 範圍 [-1.52%, +0.38%]）
- Part B 兩訊號 DXY 5d 均 < +0.5%，不影響 Part B
- 預期 Part A Sharpe 0.72 → 顯著提升；Part B 0.64 不變

跨資產貢獻：
- Repo 首次 DXY/USD direction filter 於任何資產
- 擴展 lesson #24 family（既有 implied vol forward-looking）至 spot FX index 維度
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_016_dxy_direction_breakout.config import (
    COPX016Config,
    create_default_config,
)
from trading.experiments.copx_016_dxy_direction_breakout.signal_detector import (
    COPX016DXYDirectionDetector,
)


class COPX016DXYDirectionStrategy(ExecutionModelStrategy):
    """COPX-016：DXY 方向過濾 + COPX-011 regime BOX BB Squeeze Breakout"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX016DXYDirectionDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX016Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime BOX: {config.sma_regime_ratio_min:.2f}"
                f" ≤ SMA({config.sma_regime_short})/SMA({config.sma_regime_long})"
                f" ≤ {config.sma_regime_ratio_max:.2f}"
            )
            print(
                f"  DXY 方向過濾: {config.dxy_ticker} {config.dxy_lookback}日報酬"
                f" ≤ {config.max_dxy_change:+.2%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
