"""
FXI-010: Gap-Down Capitulation + Intraday Reversal Mean Reversion

進場使用「隔夜跳空 + 日內反轉 + 回檔 + Williams %R」四重確認，
出場使用緊固定 TP/SL（TP +3.5% / SL -3.0%）。成交模型採隔日開盤市價。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_010_gap_reversal_mr.config import (
    FXI010Config,
    create_default_config,
)
from trading.experiments.fxi_010_gap_reversal_mr.signal_detector import (
    FXI010SignalDetector,
)


class FXI010Strategy(ExecutionModelStrategy):
    """FXI-010：Gap-Down 資本化 + 日內反轉均值回歸"""

    slippage_pct: float = 0.001  # 0.1% ETF standard

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI010Config):
            if config.use_gap_as_entry_trigger:
                print(f"  Gap threshold (entry trigger): Gap <= {config.gap_threshold:.1%}")
                print("  Intraday reversal: Close > Open")
                if config.require_close_above_midpoint:
                    print("  Strong reversal: Close > (High+Low)/2")
            else:
                print(
                    f"  Gap regime filter: recent {config.gap_lookback}d contains"
                    f" Gap <= {config.gap_threshold:.1%}"
                )
                print(f"  Close Position: >= {config.close_position_threshold:.0%}")
                print(
                    f"  ATR Filter: ATR({config.atr_short_period})"
                    f"/ATR({config.atr_long_period})"
                    f" > {config.atr_ratio_threshold}"
                )
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)
