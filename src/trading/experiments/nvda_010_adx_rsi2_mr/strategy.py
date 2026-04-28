"""
NVDA-010: ADX-Filtered RSI(2) Mean Reversion 策略
串接 NVDA-010 config → signal detector → 執行模型回測引擎。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_010_adx_rsi2_mr.config import (
    NVDA010Config,
    create_default_config,
)
from trading.experiments.nvda_010_adx_rsi2_mr.signal_detector import (
    NVDA010SignalDetector,
)


class NVDA010ADXRsi2MRStrategy(ExecutionModelStrategy):
    """NVDA-010：ADX-Filtered RSI(2) Mean Reversion（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA010Config):
            print(f"  ADX({config.adx_period}) >= {config.adx_threshold:.0f}（強趨勢閘門）")
            print(f"  +DI > -DI: {config.require_bullish_dmi}（多頭方向確認）")
            print(f"  趨勢過濾: Close > SMA({config.sma_trend_period})")
            print(f"  RSI({config.rsi_period}) <= {config.rsi_threshold:.0f}（短期超賣觸發）")
            print(
                f"  淺回檔範圍: {config.pullback_max:.1%} ~ {config.pullback_min:.1%}"
                f"（相對近 {config.pullback_lookback} 日高點）"
            )
            print(f"  多頭 K 棒: Close > Open = {config.bullish_close_required}")
            print(f"  冷卻期: {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
