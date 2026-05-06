"""NVDA ^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated MBPC 策略 (NVDA-018)

跨資產 + 跨策略類型首次將 lesson #24 forward-looking implied volatility derivative
regime gate 應用於 mega-cap 個股 + MBPC 框架（先前 TLT-013 / XLU-013 / GLD-015 /
USO-025 皆於 MR 框架）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_018_vxn_implied_vol_mbpc.config import (
    NVDA018Config,
    create_default_config,
)
from trading.experiments.nvda_018_vxn_implied_vol_mbpc.signal_detector import (
    NVDA018SignalDetector,
)


class NVDA018Strategy(ExecutionModelStrategy):
    """NVDA-018：NVDA-013 Att3 + ^VXN forward-looking implied vol DIRECTION gate"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA018SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA018Config):
            print(
                f"  Donchian: {config.donchian_period} 日新高，近 "
                f"{config.breakout_recency_days} 日內 breakout"
            )
            print(f"  趨勢過濾 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" ≥ {config.sma_regime_ratio_min}"
                f" × SMA({config.sma_regime_long})"
            )
            print(
                f"  淺回檔範圍: {config.pullback_max:.1%} ~ {config.pullback_min:.1%}"
                f"（相對近 {config.pullback_lookback} 日高點）"
            )
            print(
                f"  RSI({config.rsi_period}) 中性區: [{config.rsi_min:.0f}, {config.rsi_max:.0f}]"
            )
            print(f"  多頭 K 棒: Close > Open = {config.bullish_close_required}")
            if config.use_vol_regime:
                print(
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用")
            if config.use_vxn_direction_filter:
                print(
                    f"  ^VXN forward-looking IV gate: {config.vxn_ticker} "
                    f"{config.vxn_direction_lookback}d change "
                    f"<= {config.max_vxn_change:+.1f}"
                )
            else:
                print("  ^VXN forward-looking IV gate: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)
