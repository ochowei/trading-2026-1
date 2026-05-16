"""
EEM-016: Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR Strategy

在 EEM-014 Att2 BB 下軌 + 回檔上限 + WR + ClosePos + ATR + 2DD floor 框架上，
新增 **SPY 寬基 N 日絕對報酬上限** 作為 macro-context confirmation gate
（require 發達市場亦同步 drawdown，過濾中國孤立性政策/貿易衝擊持續走弱起點）。

設計理念：
- IWM-015「broad-equity-index macro context confirmation gate（非配對）」模式
  repo 第 2 次跨資產應用、首次於 EM ETF
- 與 EEM-006（EEM-SPY RS 動量主訊號，失敗）本質不同：本實驗為 SPY 絕對
  drawdown 疊加於已驗證 MR 主訊號之上的 regime gate，不涉相對強度 spread

失敗迭代記錄：（待回測填入）

最終結果：（待回測填入）

跨資產貢獻：
- repo 第 2 次「broad-equity-index macro context confirmation gate（非配對）」
  跨資產應用（繼 IWM-015），首次於 EM ETF / 首次 SPY 作 absolute drawdown
  macro anchor
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_016_global_macro_context_mr.config import (
    EEM016Config,
    create_default_config,
)
from trading.experiments.eem_016_global_macro_context_mr.signal_detector import (
    EEM016SignalDetector,
)


class EEM016Strategy(ExecutionModelStrategy):
    """EEM Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR (EEM-016)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM016Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std})")
            print(f"  回檔上限 (Cap): >= {config.pullback_cap:.0%} ({config.pullback_lookback} 日)")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日急跌下限 (2DD floor): <= {config.twoday_return_floor:.1%}")
            print(
                f"  SPY macro-context gate: {config.macro_ticker}"
                f" {config.macro_lookback} 日報酬 <= {config.macro_return_threshold:.2%}"
                "（EEM-016 核心：require 發達市場亦同步 drawdown）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
