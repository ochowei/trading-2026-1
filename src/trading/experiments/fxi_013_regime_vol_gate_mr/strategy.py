"""FXI Volatility-Regime-Gated Mean Reversion 策略 (FXI-013)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_013_regime_vol_gate_mr.config import (
    FXI013Config,
    create_default_config,
)
from trading.experiments.fxi_013_regime_vol_gate_mr.signal_detector import (
    FXI013SignalDetector,
)


class FXI013RegimeVolGateMRStrategy(ExecutionModelStrategy):
    """FXI-013：波動率 regime 閘門均值回歸（FXI-005 框架 + BB 寬度 regime 濾波）"""

    slippage_pct: float = 0.001  # 0.1% ETF 標準

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI013Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  ATR Filter: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(
                f"  波動率閘門 (Vol Regime Gate): BB({config.bb_period}, {config.bb_std}) width"
                f" / Close < {config.max_bb_width_ratio:.1%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
