"""TQQQ-028 TQQQ BB Squeeze Breakout 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_028_bb_squeeze_breakout.config import (
    TQQQ028Config,
    create_default_config,
)
from trading.experiments.tqqq_028_bb_squeeze_breakout.signal_detector import (
    TQQQ028SignalDetector,
)


class TQQQ028BBSqueezeStrategy(ExecutionModelStrategy):
    """TQQQ-028：TQQQ 自身 BB squeeze 突破（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ028SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ028Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ028Config):
            super()._print_strategy_params(config)
            return

        print("  訊號來源 (Signal source):        TQQQ 自身 (3x leveraged)")
        print(
            f"  Squeeze 閾值:                   前日 BB({config.bb_period},"
            f"{config.bb_std}) width/Close < {config.squeeze_max_bb_width:.2f}"
        )
        print(
            f"  突破確認 (Breakout):            當日 Close > BB_Upper ({config.require_breakout})"
        )
        if config.use_volume_filter:
            print(
                f"  量能確認 (Volume):              > {config.volume_multiplier}x "
                f"SMA{config.volume_sma_period}"
            )
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")
