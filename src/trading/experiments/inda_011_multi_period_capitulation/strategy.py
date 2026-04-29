"""
INDA-011: Multi-Period Capitulation-Strength Filter MR Strategy (Att3 Final)

在 INDA-010 Att3 pullback+WR+ATR+2DD floor 框架上，新增 **3 日累積跌幅 cap**
（require 3DD 不超過 -3.0%），作為多週期 capitulation-strength 過濾器。

設計理念（Att3 最終）：
- INDA-010 Att3 的 2DD floor <= -2.0% 過濾「shallow 2-day drift」（深度下限）
- INDA-011 Att3 的 3DD cap >= -3.0% 額外過濾「sustained multi-day weakness」
  （持續性上限）
- 兩維度組合捕捉「真正的 1-2 日急跌且前一日相對穩定」反轉訊號，排除
  「多日持續拖延式下跌」continuation 假反彈

失敗迭代記錄：
- Att1：3DD floor <= -3.5%（方向錯誤）— min -0.09
- Att2：3DD cap >= -3.5%（cap 過鬆，A/B 平衡破壞）— min 0.46

最終結果（Att3）：
- Part A 5/80%/Sharpe 0.55 cum +8.20%
- Part B 2/100%/std=0 cum +7.12%
- min(A,B)† 0.55（+83% vs INDA-010 Att3 的 0.30）★
- A/B cum gap 13.2% (< 30% ✓), signal ratio 1.0:1 (< 50% ✓)

跨資產貢獻：
- **Repo 首次「3DD cap」作為主要 capitulation-strength 過濾器於任何資產**
- 擴展 lesson #19 family 至「2DD floor + 3DD cap」雙維度組合（深度下限 +
  持續性上限），互補既有「1d/3d cap 組合」（DIA-012）與「2d/1d floor 組合」
  （GLD-014）變體
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_011_multi_period_capitulation.config import (
    INDA011Config,
    create_default_config,
)
from trading.experiments.inda_011_multi_period_capitulation.signal_detector import (
    INDA011SignalDetector,
)


class INDA011Strategy(ExecutionModelStrategy):
    """INDA Multi-Period Capitulation-Strength Filter MR (INDA-011)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA011Config):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
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
            print(f"  2 日急跌下限: <= {config.drop_2d_floor:.1%}（沿用 INDA-010 Att3）")
            if config.drop_3d_floor < 0.5:
                print(f"  3 日急跌下限: <= {config.drop_3d_floor:.1%}（Att1 floor 方向，已停用）")
            print(
                f"  3 日急跌上限: >= {config.drop_3d_cap:.1%}"
                "（INDA-011 Att3 核心創新：多週期持續性 cap，排除多日"
                "拖延式下跌）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
