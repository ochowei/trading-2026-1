"""
DIA-015: ^VIX Forward-Looking Implied-Vol DIRECTION Regime-Gated MR Strategy

在 DIA-012 Att2 框架（min(A,B)† 1.31）之上新增「^VIX N 日點變化上限
（CEILING）」，作為 lesson #24 family forward-looking implied vol DIRECTION
regime gate（repo 首次應用於低波動美國寬基指數 ETF）。

pre-analysis 預期結構性失敗：DIA capitulation MR 進場本質發生於 VIX-rising
fear，winners 與 losers 在 ^VIX DIRECTION 維度完全重疊，無 surgical
separator——建立 lesson #24 family 失敗邊界（鏡像 NVDA-018）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_015_vix_direction_mr.config import (
    DIA015Config,
    create_default_config,
)
from trading.experiments.dia_015_vix_direction_mr.signal_detector import (
    DIA015SignalDetector,
)


class DIA015Strategy(ExecutionModelStrategy):
    """DIA ^VIX DIRECTION Regime-Gated MR (DIA-015)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA015SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA015Config):
            print(f"  RSI 期數: {config.rsi_period} / 門檻 < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(f"  收盤位置: >= {config.close_position_threshold:.0%} of day range")
            print(f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}")
            print(f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}")
            print(
                f"  {config.vix_ticker} DIRECTION CEILING:"
                f" {config.vix_lookback}日點變化 <= {config.max_vix_change:+.2f}"
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)
