"""
DIA-018: ^VIX Implied-Vol BANDS (U-shape Regime) Gated MR Strategy

在 DIA-012 Att2 框架（min(A,B)† 1.31）之上新增 ^VIX BANDS 閘門
（lesson #24 v5 BANDS 變體，cross-strategy port from XBI-017）。
pre-analysis 預期決定性失敗（殘餘 SL VIX 22.8 被贏家 22.6/22.9 夾住），
與 DIA-015（^VIX DIRECTION）共同完成 lesson #24 family 於 DIA 之失敗邊界。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_018_vix_bands_mr.config import (
    DIA018Config,
    create_default_config,
)
from trading.experiments.dia_018_vix_bands_mr.signal_detector import (
    DIA018SignalDetector,
)


class DIA018Strategy(ExecutionModelStrategy):
    """DIA ^VIX BANDS (U-shape Regime) Gated MR (DIA-018)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA018SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA018Config):
            print(f"  RSI 期數: {config.rsi_period} / 門檻 < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(f"  收盤位置: >= {config.close_position_threshold:.0%} of day range")
            print(f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}")
            print(f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}")
            print(
                f"  {config.vix_ticker} BANDS: VIX <= {config.vix_low:.1f}"
                f" OR VIX >= {config.vix_high:.1f}（排除中段）"
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)
