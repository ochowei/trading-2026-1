"""
TQQQ 加寬出場策略 (TQQQ Wider Exit Strategy)
加寬獲利目標至 +12%，搭配追蹤停利（從高點回落 4% 出場），讓獲利奔跑。
Widens profit target to +12% with trailing stop (exit when price drops 4% from peak), letting winners run.
"""

import pandas as pd

from trading.core.base_backtester import BaseBacktester
from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.tqqq_cap_wider_exit.backtester import TrailingStopBacktester
from trading.experiments.tqqq_cap_wider_exit.config import (
    TQQQCapWiderExitConfig,
    create_default_config,
)
from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector


class TQQQCapWiderExitStrategy(BaseStrategy):
    """
    TQQQ 加寬出場策略 (TQQQ Wider Exit Strategy)

    假設：TQQQ 恐慌反彈常達 +10%~+20%，+5% 出場太早。
    Hypothesis: TQQQ capitulation bounces often reach +10%-20%; +5% exits too early.
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> BaseBacktester:
        if isinstance(config, TQQQCapWiderExitConfig):
            return TrailingStopBacktester(config)
        return super().create_backtester(config)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQCapWiderExitConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  追蹤停利 (Trailing stop):        {config.trailing_stop_pct:.0%} from peak")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

    def _print_part_report(
        self, label: str, start: str, end: str, result: dict,
        df: pd.DataFrame, config: ExperimentConfig
    ) -> None:
        """覆寫以在出場統計與交易明細中加入追蹤停利類型"""
        # 呼叫父類報表
        super()._print_part_report(label, start, end, result, df, config)

        # 在出場統計後補印追蹤停利數量
        trailing_exits = result.get("trailing_stop_exits", 0)
        if trailing_exits > 0 and result.get("trades"):
            print(f"    追蹤停利 (Trailing stop):      {trailing_exits}")
