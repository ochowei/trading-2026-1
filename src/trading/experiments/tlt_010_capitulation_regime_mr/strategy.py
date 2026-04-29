"""TLT Capitulation-Confirmed Vol-Regime-Gated Mean Reversion 策略 (TLT-010)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_010_capitulation_regime_mr.config import (
    TLT010Config,
    create_default_config,
)
from trading.experiments.tlt_010_capitulation_regime_mr.signal_detector import (
    TLT010SignalDetector,
)


class TLT010CapitulationRegimeMRStrategy(ExecutionModelStrategy):
    """TLT-010：2 日急跌確認 + 波動率 regime 閘門均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（TLT 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT010Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  波動率閘門 (Vol Regime Gate): BB({config.bb_period}, {config.bb_std}) width"
                f" / Close < {config.max_bb_width_ratio:.1%}"
            )
            print(
                f"  急跌確認 (2D Capitulation): {config.two_day_decline_lookback}d return"
                f" <= {config.two_day_decline_threshold:.1%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
