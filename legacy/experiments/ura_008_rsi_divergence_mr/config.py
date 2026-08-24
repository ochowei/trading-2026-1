"""
URA RSI Bullish Divergence + Pullback + WR Mean Reversion 配置 (URA-008)

基於 URA-002 進場架構（10日回檔 10-20% + WR(10) ≤ -80），加入 RSI(14)
bullish hook divergence 過濾器，捕捉「RSI 已從 oversold 低點回升」的 capitulation
尾聲訊號，移除「RSI 仍在下探」的持續下跌訊號。

Pattern source: SIVR-015 Att1（lesson #20b）。URA 與 SIVR 同為 2.3% 日波動 + 10 日
pullback 框架，且兩段 Part A/B 皆活躍 MR regime，符合 20b 全部四項條件：
  - 日波動 2.34%（2-3% 範圍）
  - 已驗證 pullback+WR 均值回歸框架（URA-001/002）
  - Pullback lookback 10 日（≤10 日要求）
  - URA-004 Part A Sharpe 0.41 / Part B 0.39（兩段活躍 MR regime）

設計理念：
  - 三次迭代摸索進場結構：
    Att1: URA-004 base（pullback+RSI(2)+2DD）+ hook → 僅 2/2 訊號（2DD 與 hook 矛盾）
    Att2: pullback+RSI(2)+hook（移除 2DD）→ 4/2 訊號（RSI(2)<15 過嚴）
    Att3: pullback+WR(10)+hook（URA-002 base + hook，同 SIVR-015 結構）→ 當前版本
  - Att3 採取與 SIVR-015 完全一致的基底：WR(10) ≤ -80 的 10 日超賣較 RSI(2) 寬鬆，
    保留更多訊號供 hook 過濾器作用，對應 URA-002 的 24/16 訊號基數

Based on URA-002 (10-day pullback 10-20% + WR(10) ≤ -80), adds RSI(14) bullish
hook filter: requires RSI(14) to have risen from recent 5-day low by ≥ H points
where the low itself was ≤ 35 (oversold context).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URARSIDivergenceMRConfig(ExperimentConfig):
    """URA RSI Bullish Divergence + Pullback+WR 均值回歸參數"""

    # 進場指標（同 URA-002）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔 ≤ 20%
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 新增：RSI(14) bullish hook 過濾（移植 SIVR-015 Att1 參數）
    rsi_period: int = 14
    rsi_hook_lookback: int = 5  # 觀察過去 N 日內 RSI 最低點
    rsi_hook_delta: float = 3.0  # RSI 需自近期低點回升 ≥ H 點
    rsi_hook_max_min: float = 35.0  # 近期 RSI 低點須曾 ≤ 此水位（oversold）

    cooldown_days: int = 10


def create_default_config() -> URARSIDivergenceMRConfig:
    return URARSIDivergenceMRConfig(
        name="ura_008_rsi_divergence_mr",
        experiment_id="URA-008",
        display_name="URA RSI Bullish Divergence + Pullback+WR MR",
        tickers=["URA"],
        data_start="2010-11-05",
        profit_target=0.060,  # +6.0%
        stop_loss=-0.055,  # -5.5%
        holding_days=20,
    )
