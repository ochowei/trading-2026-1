"""
FXI-016: USDCNH Direction Filter on FXI-ASHR Cross-Asset Divergence MR
Uses ExecutionModelBacktester (next-open + 0.1% slippage + pessimistic intrabar).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_016_usdcnh_direction_mr.config import (
    FXI016Config,
    create_default_config,
)
from trading.experiments.fxi_016_usdcnh_direction_mr.signal_detector import (
    FXI016USDCNHDirectionDetector,
)


class FXI016Strategy(ExecutionModelStrategy):
    """FXI USDCNH Direction-Gated Cross-Asset Divergence MR (FXI-016)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI016USDCNHDirectionDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI016Config):
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", cap <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%} of day range")
            print(
                f"  ATR Band: {config.atr_ratio_floor} < ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" <= {config.atr_ratio_ceiling}"
            )
            print(
                f"  FXI-{config.anchor_ticker} divergence: FXI({config.rel_lookback}d)"
                f" - {config.anchor_ticker}({config.rel_lookback}d)"
                f" >= {config.min_rel_return:+.2%}"
            )
            print(
                f"  USDCNH 方向: {config.usdcnh_lookback}日報酬"
                f" <= {config.max_usdcnh_change:.2%}（{config.usdcnh_ticker}）"
            )
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)
