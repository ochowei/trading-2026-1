"""
COPX RSI Bullish Divergence + Pullback+WR+ATR Mean Reversion 配置 (COPX-009)

基於 COPX-007（20日回檔 10-20% + WR(10) ≤ -80 + ATR(5)/ATR(20) > 1.05），
加入 RSI(14) bullish hook divergence 過濾器。

Hypothesis: COPX-007 Part A 有 21 訊號（WR 76.2%），Part B 僅 10 訊號（WR 80.0%），
訊號頻率差距 110%，累計報酬差距 86%。COPX-007 在 2020 COVID / 2022 銅價下行週期中
部分訊號觸發於 RSI 仍在下探時（延續性下跌結構）；bullish hook 過濾器可選擇性移除這些
訊號，提升 Part A 品質同時保留 Part B 真正的 capitulation 末端訊號，改善 A/B 平衡。

此為 SIVR-015 bullish divergence 跨資產泛化測試：COPX 日波動 2.25%（vs SIVR 2.3-2.5%）
同屬「中高波動 + 已驗證 pullback+WR 框架」類別，最符合 SIVR-015 的泛化條件。

## 三次迭代結果（全部未勝過 COPX-007 min 0.45）

Att1 (ATR 1.05 + hook lookback 5 / delta 3 / max_min 35)：
  Part A Sharpe -0.50 (6 訊號 WR 33.3% 累計 -11.42%) / Part B 0.00 (3 訊號 WR 100% 累計 10.87%)
  → min(A,B) -0.50；hook 過濾反移除 Part A 好訊號（COPX-007 的 21→6 訊號中 WR 從 76.2% 崩至 33.3%）

Att2 (ATR 1.05 + hook lookback 10 / delta 3 / max_min 35)：
  Part A Sharpe 0.00 (7 訊號 WR 57.1% 累計 -0.49%) / Part B 0.00 (4 訊號 WR 100% 累計 14.75%)
  → min(A,B) 0.00；延長 lookback 略改善但仍無法恢復 COPX-007 品質

Att3 (無 ATR + hook lookback 10 / delta 3 / max_min 35)★最終版：
  Part A Sharpe 0.15 (14 訊號 WR 64.3% 累計 7.47%) / Part B 0.57 (5 訊號 WR 80% 累計 9.43%)
  → min(A,B) 0.15；移除 ATR 恢復部分訊號但 Part A WR 仍低於 COPX-007 的 76.2%

## 失敗根因分析

RSI(14) bullish hook divergence **不適用** COPX 20日回檔+WR(10) 框架：
- SIVR-015 成功條件：10日回檔 7-15%（短窗口） + WR(10)，5日 RSI 低點對應快速 capitulation
- COPX-007 失敗原因：20日回檔 10-20%（長窗口）導致延續性下跌持續 15-30 日，
  RSI(14) 在此窗口內常多次 hook up-down。5 日 hook lookback 捕捉的是局部雜訊，
  10 日 lookback 仍無法對齊 20 日回檔的整體動能下探結構
- 跨資產泛化邊界：hook divergence 僅對「**短回檔窗口** (≤10日) + **快速 capitulation** 」資產有效
- COPX-003 框架特性為「**慢磨下跌** + 最終恐慌反彈」，divergence 訊號在此結構下為雜訊

此結果擴展 cross_asset_lessons §20b 的有效邊界：需同時符合（a）中高波動 2-3%、
（b）pullback+WR 框架、且 **（c）回檔回看窗口 ≤10 日** 三個條件。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX009Config(ExperimentConfig):
    """COPX-009 RSI Bullish Divergence + Pullback+WR+ATR 均值回歸參數"""

    # 進場指標（同 COPX-007）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0
    cooldown_days: int = 12

    # ATR 波動率飆升過濾（Att3 最終：停用 ATR 過濾以隔離 RSI hook 貢獻）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 0.0
    enable_atr_filter: bool = False

    # RSI(14) bullish hook 過濾（Att3 最終：lookback 10 日對齊 20 日回檔框架）
    rsi_period: int = 14
    rsi_hook_lookback: int = 10
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0


def create_default_config() -> COPX009Config:
    return COPX009Config(
        name="copx_009_rsi_divergence_mr",
        experiment_id="COPX-009",
        display_name="COPX RSI Bullish Divergence + Pullback+WR+ATR MR",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.045,
        holding_days=20,
    )
