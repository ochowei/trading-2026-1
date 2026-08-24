"""
TQQQ-017：恐慌抄底 + 日內反轉確認策略
(TQQQ Capitulation + Intraday Recovery Confirmation Strategy)

沿用 TQQQ-010 的 TP/SL/持倉/成交模型，進場加入 ClosePos >= 0.30 過濾器。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_017_cap_reversal_confirm.config import (
    TQQQ017Config,
    create_default_config,
)
from trading.experiments.tqqq_017_cap_reversal_confirm.signal_detector import (
    TQQQ017SignalDetector,
)


class TQQQ017Strategy(ExecutionModelStrategy):
    """TQQQ-017：恐慌抄底 + 日內反轉確認"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ017SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQ017Config):
            print(
                f"  回撤 (Drawdown): {config.drawdown_lookback}日高點回撤"
                f" <= {config.drawdown_threshold:.0%}"
            )
            print(f"  RSI: RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  成交量 (Volume): Volume > {config.volume_multiplier}x"
                f" SMA({config.volume_sma_period})"
            )
            if config.close_position_threshold > 0:
                print(
                    f"  日內反轉 (ClosePos): (Close-Low)/(High-Low)"
                    f" >= {config.close_position_threshold:.0%}"
                )
            if config.enable_two_day_filter:
                print(f"  2日加速 (2-day return): <= {config.two_day_return_threshold:.0%}")
            if config.prev_rsi_threshold > 0:
                print(f"  前日超賣 (Prev RSI({config.rsi_period})): < {config.prev_rsi_threshold}")
            print(f"  獲利目標 (Profit target): +{config.profit_target:.0%}")
            print(f"  停損 (Stop-loss): {config.stop_loss:.0%}")
            print(f"  最長持倉 (Max holding): {config.holding_days} 天")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
