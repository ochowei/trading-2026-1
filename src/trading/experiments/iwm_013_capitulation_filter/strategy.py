"""
IWM-013: Capitulation-Depth Filter Mean Reversion Strategy
        (Att3 final = RSI Oscillator Depth)

在 IWM-011 Att2 框架（min(A,B) Sharpe 0.52，IWM 全域最佳）上嘗試三類
capitulation strength 過濾維度，最終發現 oscillator depth (RSI(2) threshold)
為對 IWM 小型股寬基 ETF 最有效的 capitulation 度量維度。

設計理念（Att3 最終）：
- IWM Part A/B losers 在 raw return 維度（1d、3d）與 winners 高度重疊（Att1/Att2
  失敗），但在 oscillator 維度（RSI(2)）有清晰分隔：losers 集中於 RSI 8-10
  區間（2019-08-02 RSI=8.2 / 2025-03-04 RSI=9.1），全部 Part B winners
  RSI <= 5.0、全部 Part A winners RSI <= 7.9
- RSI(2) 較 raw return 更能捕捉「多日累積動能耗竭」的 capitulation 強度
- IWM-011 的 RSI < 10 閾值雖已篩選 oversold，但仍允許 RSI 7-9 區間的「弱
  oversold」訊號通過。RSI < 8 排除這類訊號

跨資產延伸（lesson #19 family，2026-04-26 第 4 次成功）：
- DIA-012 (1.0% vol)：1d cap -2% + 3d cap -7% 雙維度，min(A,B)† 1.31
- SPY-009 (1.2% vol)：1d FLOOR + 3d cap，min(A,B)† 6.56
- EWJ-005 (1.15% vol)：1d floor 單維度，min(A,B)† 0.70
- IWM-013 (1.5-2.0% vol)：**RSI(2) oscillator depth**（repo 首次以 oscillator
  維度替代 raw return 維度，首次小型股寬基 ETF），min(A,B)† 0.59
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_013_capitulation_filter.config import (
    IWM013Config,
    create_default_config,
)
from trading.experiments.iwm_013_capitulation_filter.signal_detector import (
    IWM013SignalDetector,
)


class IWM013Strategy(ExecutionModelStrategy):
    """IWM Capitulation-Depth Filter MR (IWM-013)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM013Config):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
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
                print(f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}（IWM-013 cap 維度）")
            else:
                print("  1 日急跌上限 (1d cap): 停用 (Att1 失敗，Att2 改用 floor)")
            if config.threeday_return_cap > -0.50:
                print(f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}（IWM-013 cap 維度）")
            else:
                print("  3 日急跌上限 (3d cap): 停用 (Att1 失敗，Att2 改用 floor)")
            tf = getattr(config, "threeday_return_floor", 0.0)
            if tf < 0:
                print(
                    f"  3 日急跌下限: <= {tf:.1%}"
                    "（IWM-013 floor 維度：require 3d 深度，過濾 shallow drift 假訊號）"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
