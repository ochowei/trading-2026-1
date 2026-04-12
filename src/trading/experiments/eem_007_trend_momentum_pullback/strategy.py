"""
EEM-007: Regime-Filtered Mean Reversion
(EEM 牛市政權過濾均值回歸)

Att1-2: 趨勢動量回調 → 市場狀態依賴過強（Part B Sharpe -0.32/-0.37）
Att3: 策略轉向 — 在 SMA(200) 牛市政權中做 RSI(2) 均值回歸
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_007_trend_momentum_pullback.config import (
    EEM007Config,
    create_default_config,
)
from trading.experiments.eem_007_trend_momentum_pullback.signal_detector import (
    EEM007SignalDetector,
)


class EEM007Strategy(ExecutionModelStrategy):
    """EEM 牛市政權過濾均值回歸 (EEM-007)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM007SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM007Config):
            print(f"  牛市政權: SMA({config.regime_sma_period})")
            print(f"  超賣: RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  急跌: {config.decline_days}日跌幅 >= {config.decline_threshold:.1%}")
            print(f"  日內反轉: ClosePos >= {config.close_pos_threshold:.0%}")
            print(
                f"  波動率飆升: ATR({config.atr_short})/ATR({config.atr_long})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
