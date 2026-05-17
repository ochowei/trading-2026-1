"""FXI–CNY Currency-Regime-Gated MR 策略 (FXI-015)
Uses ExecutionModelBacktester (next-open + 0.1% slippage + pessimistic intrabar).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_015_cny_regime_mr.config import (
    FXI015Config,
    create_default_config,
)
from trading.experiments.fxi_015_cny_regime_mr.signal_detector import (
    FXI015SignalDetector,
)


class FXI015CnyRegimeMRStrategy(ExecutionModelStrategy):
    """FXI-015：FXI-014 Att2 + FXI–CNY 貨幣 regime gate"""

    slippage_pct: float = 0.001  # 0.1%（FXI 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI015SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI015Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" ≥ {abs(config.pullback_threshold):.0%}"
                f", cap ≤ {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  ATR Band: {config.atr_ratio_floor} < ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) ≤ {config.atr_ratio_ceiling}"
            )
            if config.use_cny_ceiling:
                print(
                    f"  CNY CEILING gate: {config.cny_ticker} "
                    f"{config.cny_lookback}d return ≤ {config.max_cny_return:+.1%}"
                )
            if config.use_cny_divergence:
                print(
                    f"  CNY DIVERGENCE gate: FXI−{config.cny_ticker} "
                    f"{config.cny_lookback}d return ≥ {config.min_relative_return:+.1%}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
