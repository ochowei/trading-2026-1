"""TLT Sustained Low-Volatility Regime Mean Reversion 策略 (TLT-012)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_012_sustained_regime_mr.config import (
    TLT012Config,
    create_default_config,
)
from trading.experiments.tlt_012_sustained_regime_mr.signal_detector import (
    TLT012SignalDetector,
)


class TLT012SustainedRegimeMRStrategy(ExecutionModelStrategy):
    """TLT-012：多日持續波動率 regime 閘門均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（TLT 高流動 ETF，同 TLT-007）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT012Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            mode_label = {
                "all": f"過去 {config.trajectory_lookback + 1} 日 BB 寬度皆 <",
                "mean": f"過去 {config.trajectory_lookback + 1} 日 BB 寬度均值 <",
                "contracting": (
                    f"當日 BB 寬度 < {config.max_bb_width_ratio:.1%} AND 當日 BB 寬度 <= "
                    f"{config.trajectory_lookback} 日前 BB 寬度（不擴張）"
                ),
            }.get(config.trajectory_mode, config.trajectory_mode)
            print(
                f"  Regime 閘門 (Vol Regime Gate, mode={config.trajectory_mode}): "
                f"BB({config.bb_period}, {config.bb_std}) 寬度/Close {mode_label}"
                f" {config.max_bb_width_ratio:.1%}"
                if config.trajectory_mode != "contracting"
                else f"  Regime 閘門 (Vol Regime Gate, mode={config.trajectory_mode}): {mode_label}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
