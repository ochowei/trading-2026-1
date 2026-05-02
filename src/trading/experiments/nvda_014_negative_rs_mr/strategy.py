"""
NVDA-014: Negative Relative Strength Mean Reversion (Pairs MR vs SMH)

當 NVDA 相對半導體板塊（SMH）顯著跑輸時買進，預期相對均值回歸。
NVDA-006（正向 RS 動量延續）的反向探索：repo 第一次以負向相對強度作為
**主訊號** 的均值回歸實驗。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_014_negative_rs_mr.config import (
    NVDA014Config,
    create_default_config,
)
from trading.experiments.nvda_014_negative_rs_mr.signal_detector import NVDA014Detector


class NVDANegativeRSMRStrategy(ExecutionModelStrategy):
    """NVDA-014：Negative Relative Strength Pairs Mean Reversion（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA014Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA014Config):
            print(
                f"  負向相對強度 (Negative RS): NVDA - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" ≤ {config.relative_strength_max:+.0%}"
            )
            print(
                f"  深回檔 (Deep Pullback): ≥ {config.pullback_min:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(
                f"  波動 regime gate (Vol Regime):"
                f" ATR({config.atr_regime_short})/ATR({config.atr_regime_long})"
                f" ≤ {config.vol_regime_max_ratio:.2f}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
