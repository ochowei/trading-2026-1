"""
INDA-014: DXY Direction Filter on Multi-Period Capitulation MR Strategy

在 INDA-011 Att3（Multi-Period Capitulation-Strength Filter MR，
min(A,B)† 0.55）框架之上，疊加「DXY N 日報酬 <= max_dxy_change」
USD 強度方向過濾（lesson #24 family DIRECTION 變體）。

結果：三次迭代全部 FAIL（Att1 min 0.37 / Att2 †3.56 REJECT / Att3
min 0.37），INDA-011 Att3（min 0.55）維持全域最優。詳見 config.py
docstring 完整迭代與失敗分析。

根因：INDA-011 Att3 殘餘 1 筆 Part A SL（2022-09-16 Fed CPI shock）經
「利率 / 風險」通道傳導，**非** USD 強度通道——signal-day DXY
3d/5d/10d = -0.05%/+0.70%/+0.06% 全部位於 winners 分布正中央，任何
lookback / 方向皆無 surgical 切點；多筆 INDA winners 反而發生於 USD
走強期，與原始假設相反。

跨資產貢獻（負面結果，repo 重要邊界發現）：
- **REJECT COPX-016 開放跨資產假設**「DXY direction → EM ETFs INDA」
  於單一國家 EM 股票 ETF MR 框架
- USD→商品 傳導（COPX 有效）≠ USD→單一國家 EM 股票 傳導（INDA
  capitulation SL 為利率 / 風險衝擊驅動）
- 擴展 lesson #24 family DIRECTION 邊界 + 平行 lesson #6 / COPX-014
  「winners/losers 重疊無 surgical 切點」失敗家族
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_014_dxy_direction_mr.config import (
    INDA014Config,
    create_default_config,
)
from trading.experiments.inda_014_dxy_direction_mr.signal_detector import (
    INDA014SignalDetector,
)


class INDA014Strategy(ExecutionModelStrategy):
    """INDA DXY Direction Filter MR (INDA-014)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價，同 INDA-011）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA014Config):
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
            print(f"  3 日急跌上限: >= {config.drop_3d_cap:.1%}（沿用 INDA-011 Att3）")
            print(
                f"  DXY 方向過濾: {config.dxy_ticker} {config.dxy_lookback}日報酬"
                f" <= {config.max_dxy_change:+.2%}"
                "（INDA-014 核心創新：USD 強度方向過濾）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
