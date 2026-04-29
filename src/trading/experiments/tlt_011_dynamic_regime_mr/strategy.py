"""TLT Dynamic BB-Width Percentile Regime MR 策略 (TLT-011)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_011_dynamic_regime_mr.config import (
    TLT011Config,
    create_default_config,
)
from trading.experiments.tlt_011_dynamic_regime_mr.signal_detector import (
    TLT011SignalDetector,
)


class TLT011DynamicRegimeMRStrategy(ExecutionModelStrategy):
    """TLT-011：動態 BB 寬度分位數 regime 閘門均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（TLT 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT011Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  動態波動率閘門 (Dynamic Vol Gate): BB({config.bb_period}, {config.bb_std})"
                f" width/Close {config.bb_width_pctile_lookback}d pctile rank <="
                f" {config.max_bb_width_pctile_rank:.0%}"
            )
            if config.enable_absolute_backup:
                print(
                    f"  絕對波動率上限 (Absolute Backup): BB width/Close <"
                    f" {config.max_bb_width_ratio_absolute:.1%}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
