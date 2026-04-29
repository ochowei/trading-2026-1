"""
NVDA-011: Capitulation-Depth Filter Mean Reversion Strategy
        (Cross-asset port from IWM-013 Att3 SUCCESS)

跨資產延伸（lesson #19 family，repo 第 5 次 capitulation-depth filter 嘗試，
首次高波動 >3% vol 單一個股測試）：
- DIA-012 (1.0% vol)：1d cap -2% + 3d cap -7% 雙維度，min(A,B)† 1.31
- SPY-009 (1.2% vol)：1d FLOOR + 3d cap，min(A,B)† 6.56
- EWJ-005 (1.15% vol)：1d floor 單維度，min(A,B)† 0.70
- IWM-013 (1.5-2.0% vol)：RSI(2) oscillator depth，min(A,B)† 0.59
- **NVDA-011 (3.26% vol)**：RSI(2) oscillator depth on high-vol single stock

NVDA vol 縮放（vs IWM 1.7-2.0x）：
- 2DD: -2.5% → -4.5%
- TP: +4% → +7%
- SL: -4.25% → -7%
- Holding: 20d → 15d
- Cooldown: 5d → 8d
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_011_capitulation_filter.config import (
    NVDA011Config,
    create_default_config,
)
from trading.experiments.nvda_011_capitulation_filter.signal_detector import (
    NVDA011SignalDetector,
)


class NVDA011Strategy(ExecutionModelStrategy):
    """NVDA Capitulation-Depth Filter MR (NVDA-011)"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA011Config):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: <= {config.decline_threshold:.1%}（{config.decline_lookback} 日）"
            )
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            if config.oneday_return_cap > -0.50:
                print(
                    f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}（DIA-012/SPY-009 cap 維度）"
                )
            else:
                print("  1 日急跌上限 (1d cap): 停用")
            if config.threeday_return_cap > -0.50:
                print(f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}（DIA-012 cap 維度）")
            else:
                print("  3 日急跌上限 (3d cap): 停用")
            tf = getattr(config, "threeday_return_floor", 0.0)
            if tf < 0:
                print(f"  3 日急跌下限: <= {tf:.1%}（USO/EEM/INDA/VGK floor 維度）")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
