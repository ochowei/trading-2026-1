"""TQQQ-022: QQQ-SPY Cross-Asset Divergence FLOOR Regime-Gated Capitulation 策略

跨**策略類型**首次將 cross-asset divergence regime gate（FLOOR 方向，
mirror TLT-014 / TSLA-017 underperformance-as-weakness）應用於 3x 槓桿
科技 ETF + extreme capitulation framework。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_022_qqq_spy_divergence_cap.config import (
    TQQQ022Config,
    create_default_config,
)
from trading.experiments.tqqq_022_qqq_spy_divergence_cap.signal_detector import (
    TQQQ022QQQSPYDivergenceDetector,
)


class TQQQ022QQQSPYDivergenceStrategy(ExecutionModelStrategy):
    """TQQQ-022：QQQ-SPY 跨資產背離 FLOOR + 波動率 regime + capitulation 抄底"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ022QQQSPYDivergenceDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ022Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ022Config):
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
        if config.use_divergence_filter:
            print(
                f"  跨資產背離 FLOOR:               {config.qqq_ticker} - {config.spy_ticker} "
                f"{config.divergence_lookback}d 報酬差 >= {config.min_relative_return:+.2%}"
            )
        else:
            print("  跨資產背離: 已停用")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")
