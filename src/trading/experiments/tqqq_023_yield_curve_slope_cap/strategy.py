"""TQQQ-023: Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy 策略

跨**資產類別**首次將 yield curve slope velocity（^TYX - ^TNX）regime gate
（TLT-017 lesson #24 family v10）自 rate-direct asset (TLT) 移植至 leveraged
tech ETF (TQQQ) — long-duration valuation 機制間接傳導假設驗證。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_023_yield_curve_slope_cap.config import (
    TQQQ023Config,
    create_default_config,
)
from trading.experiments.tqqq_023_yield_curve_slope_cap.signal_detector import (
    TQQQ023YieldCurveSlopeDetector,
)


class TQQQ023YieldCurveSlopeStrategy(ExecutionModelStrategy):
    """TQQQ-023：恐慌抄底 + 波動率 regime + yield curve slope velocity（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ023YieldCurveSlopeDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ023Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ023Config):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(
            f"  波動率閘門 (Vol Regime Gate):    BB({config.bb_period}, {config.bb_std}) width"
            f" / Close < {config.max_bb_width_ratio:.2f}"
        )
        print(
            f"  進場前回撤 (Prior DD Filter):    DD(T-{config.prior_drawdown_lookback}) "
            f"<= {config.prior_drawdown_threshold:.0%}"
        )
        if config.use_slope_change_filter:
            print(
                f"  殖利率曲線速度 (Slope Vel):    "
                f"({config.long_yield_ticker} - {config.short_yield_ticker}) "
                f"{config.slope_lookback}d 變化 <= +{config.max_slope_change:.3f}"
            )
        if config.use_slope_level_filter:
            print(
                f"  殖利率曲線水準 (Slope Level): "
                f"({config.long_yield_ticker} - {config.short_yield_ticker}) "
                f"<= +{config.max_slope_level:.3f}"
            )
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")
