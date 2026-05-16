"""
INDA-013: Forward-Looking Implied-Vol Regime-Gated Multi-Period
Capitulation MR Strategy

在 INDA-011 Att3（Multi-Period Capitulation-Strength Filter MR，
min(A,B)† 0.55，全域最優）框架之上，疊加 lesson #24 family
forward-looking implied-vol regime gate（^MOVE 利率通道 / ^VIX
風險通道），目標 surgical 過濾唯一殘餘 Part A SL 2022-09-16
（Fed CPI shock）。

PRE-ANALYSIS GATE 預測 DOCUMENTED-FAILURE：2022-09-16 SL 在 ^MOVE
LEVEL/CEILING 與 ^VIX 全維度皆與 winners 結構性交錯，僅 ^MOVE 3d
FLOOR 為 n=7 post-hoc 單點分離器（依 EEM-016 標準應 REJECT）。
詳見 config.py docstring 完整 pre-analysis、三次迭代與失敗分析。

跨資產貢獻（負面結果，repo 邊界發現）：
- lesson #24 family 首次應用於單一國家 EM 股票 ETF
- 確認 INDA 殘餘 2022-09-16 SL 為 idiosyncratic Fed-shock，跨
  DXY（INDA-012）+ ^MOVE + ^VIX 三維度皆 non-separable
- INDA 加入 TSM-012 / EWJ-006 / EEM-016「idiosyncratic non-separable
  residual SL」家族，擴展 lesson #24 family DIRECTION 邊界
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_013_implied_vol_regime_mr.config import (
    INDA013Config,
    create_default_config,
)
from trading.experiments.inda_013_implied_vol_regime_mr.signal_detector import (
    INDA013SignalDetector,
)


class INDA013Strategy(ExecutionModelStrategy):
    """INDA Implied-Vol Regime-Gated MR (INDA-013)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價，同 INDA-011/012）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA013Config):
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
                f"  IV regime gate: {config.iv_ticker} {config.iv_mode}"
                f" (lookback={config.iv_lookback}d, threshold={config.iv_threshold:+.1f})"
                "（INDA-013 核心創新：lesson #24 forward-looking implied-vol）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
