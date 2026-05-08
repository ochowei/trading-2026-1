"""
NVDA-019: Failed Breakdown Reversal Mean Reversion 策略

repo 首次將 Failed Breakdown Reversal 模式作為 MR 主進場訊號於 NVDA。
搭配 lesson #22 雙重 regime gate（SMA trend + ATR vol）作為品質過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_019_failed_breakdown_mr.config import (
    NVDA019Config,
    create_default_config,
)
from trading.experiments.nvda_019_failed_breakdown_mr.signal_detector import (
    NVDA019FailedBreakdownDetector,
)


class NVDA019FailedBreakdownStrategy(ExecutionModelStrategy):
    """NVDA-019：Failed Breakdown Reversal MR 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA019FailedBreakdownDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA019Config):
            print(
                f"  Donchian Lower: {config.donchian_period} 日，"
                f"breakdown lookback {config.breakdown_lookback_days} 日"
            )
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
                print("  波動 regime: 已停用")
            print(f"  陽線確認: Close > Open = {config.require_bullish_close}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
