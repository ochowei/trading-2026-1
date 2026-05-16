"""TQQQ-027 QQQ Single-Day Momentum-Reversal MR → Trade TQQQ 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_027_qqq_single_day_reversal.config import (
    TQQQ027Config,
    create_default_config,
)
from trading.experiments.tqqq_027_qqq_single_day_reversal.signal_detector import (
    TQQQ027SignalDetector,
)


class TQQQ027QqqReversalStrategy(ExecutionModelStrategy):
    """TQQQ-027：QQQ 單日動量反轉 → 交易 TQQQ（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ027SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ027Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ027Config):
            super()._print_strategy_params(config)
            return

        print("  訊號來源 (Signal source):        QQQ (1x NASDAQ ETF)")
        print("  交易標的 (Trade target):         TQQQ (3x leveraged)")
        print(f"  單日急跌門檻 (QQQ ROC1):         <= {config.qqq_roc1_threshold:.2f}%")
        print(f"  日內反轉門檻 (QQQ ClosePos):     >= {config.qqq_min_closepos:.2f}")
        if config.use_qqq_volume_filter:
            print(
                f"  QQQ 量能確認:                   > {config.qqq_volume_multiplier}x "
                f"SMA{config.qqq_volume_sma_period}"
            )
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")
