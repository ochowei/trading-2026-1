"""COPX-013：Macro-Confirmed Vol-Adaptive Capitulation MR 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_013_macro_confirmed_mr.config import (
    COPX013Config,
    create_default_config,
)
from trading.experiments.copx_013_macro_confirmed_mr.signal_detector import (
    COPX013SignalDetector,
)


class COPX013Strategy(ExecutionModelStrategy):
    """COPX-013：COPX-007 框架 + SPY broad-market macro context confirmation gate"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX013Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            print(
                f"  Macro confirmation: {config.macro_ticker}"
                f" {config.macro_lookback}d return <= {config.max_spy_return:+.1%}"
            )
            print(
                f"  VIX direction filter: {config.vix_ticker}"
                f" {config.vix_direction_lookback}d change <= {config.max_vix_change:+.1f}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
