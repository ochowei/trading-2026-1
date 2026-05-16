"""
CIBR-016: ^VIX Implied-Vol Regime BANDS Filter Mean Reversion 配置

策略方向（Strategy Direction）：
    在 CIBR-008 Att2（BB 下軌 + 回檔上限混合進場 MR，含殘餘 Part A SL）
    基礎上，疊加 **^VIX forward-looking implied-vol BANDS regime gate**，
    直接移植 XBI-017 Att1（XBI 全域最優突破，min(A,B) 0.46 → 0.64，+39%）
    的 lesson #24 family BANDS 變體。

    **Repo 第 2 次 lesson #24 family BANDS 變體跨資產驗證**（XBI-017 後首次），
    **首次於網路安全板塊 ETF（CIBR 1.53% vol）**。XBI-017 的 U 型 regime
    假說：capitulation MR 僅在低 VIX（板塊孤立型下跌、broad 健康）或高 VIX
    （broad panic systematic V-bounce）兩極端 regime 結構性有效；中等 VIX
    帶（complacency creep）MR 失效。本實驗測試此跨資產假說是否在 CIBR
    複製。

================================================================================
強制前置 trade-level 預分析（pre-analysis gate，建構前執行，2026-05-16）
================================================================================
CIBR-008 Att2（current data）逐筆訊號 signal-day ^VIX close：

  Part A（binding，Sharpe 0.79）:
    2019-08-05 TP  VIX 24.59
    2019-10-02 TP  VIX 20.56
    2020-02-24 SL  VIX 25.03   ← 唯一殘餘 SL（COVID onset，1d -3.54%）
    2020-10-30 TP  VIX 38.02
    2022-09-01 TP  VIX 25.56
    2023-03-13 TP  VIX 26.52
  Part B（Sharpe 4.38，全勝）:
    2024-02-21 TP  VIX 15.34
    2024-04-16 EXP VIX 18.40
    2024-08-02 TP  VIX 23.39
    2025-08-01 EXP VIX 20.38
    2025-11-18 TP  VIX 24.69

**核心預判（pre-analysis verdict = REJECT 方向）**：唯一殘餘 SL
（2020-02-24，VIX 25.03）與 Part A winners VIX 24.59（2019-08-05）/
25.56（2022-09-01）/ 26.52（2023-03-13）**完全交錯**（左右 ≤0.5pt 間隙）。
**不存在任何 VIX BANDS 門檻對（low/high）能外科式隔離 SL 而保留鄰近 winners**。
XBI-017 的 U 型假說（SL 集中於中等 VIX complacency 帶、winners 在兩極端）
**在 CIBR 不複製**——CIBR 唯一 capitulation-MR SL 為 COVID-onset 落於
moderate-high VIX（25.03）且嵌於 winner cluster 中段，且該 SL 已被
CIBR-014 Att2 之 realized-return 1d-cap（1d -3.54%）外科式移除。
與 EEM-014「2DD filter 方向資產相依、SL 與 winners 維度交錯」失敗家族同構。
本實驗為「pre-analysis 預測 → backtest 確認」之 documented-failure
（SOXL-013 / TSM-012 / EWJ-006 既往慣例）。

================================================================================
基礎（同 CIBR-008 Att2，含殘餘 SL；類比 XBI-017 建於 XBI-015 Att2）
================================================================================
- Close <= BB(20, 2.0) 下軌
- 10 日高點回檔 >= -12%（崩盤隔離）
- Williams %R(10) <= -80
- ClosePos >= 40%
- ATR(5)/ATR(20) > 1.15（panic FLOOR）
- 冷卻 8 日
- TP +3.5% / SL -4.0% / 18 天，0.1% 滑價（成交模型：隔日開盤市價進場）

================================================================================
CIBR-016 新增（^VIX BANDS gate；XBI-017 跨資產移植）
================================================================================
- 訊號通過條件：VIX <= vix_low_threshold OR VIX > vix_high_threshold
  （排除中等 VIX 帶 [vix_low, vix_high]，與 XBI-017 同向）

迭代紀錄（pre-analysis 預測全部 FAIL vs CIBR 全域最優 CIBR-014 Att2† 4.08）：
  Att1（vix_low=17.0, vix_high=22.0，XBI-017 Att1 參數直接移植）
    預判：SL 2020-02-24 VIX 25.03 > 22 → 通過（SL 未被過濾）；
    winners VIX 18.40/20.38/20.56 落於 (17,22] → 被過濾（移除 winners）。
    方向相反，degrade。
  Att2（vix_low=24.7, vix_high=25.4，post-hoc 嘗試 bracket SL）
    SL VIX 25.03 ∈ (24.7,25.4] → 過濾；winners 24.59≤24.7、25.56>25.4
    → 保留。看似全勝但為退化型「單 SL 0.7pt notch」post-hoc curve-fit，
    無理論依據與泛化性（XBI-017 17/22 為理論 U-shape），依嚴謹標準 REJECT。
  Att3（穩健性 ablation：band 移位 ±0.5pt，如 (24.0,25.0]）
    結果完全翻轉（重新放回 SL 或誤殺 winner），確認無泛化 VIX-BANDS
    regime 結構，最終 REJECT。

================================================================================
基準對照（CIBR 全域最優 CIBR-014 Att2 ★ min(A,B)† 4.08）
================================================================================
- CIBR-008 Att2 base（current data）: Part A 6/83.3%/0.79；Part B 5/100%/4.38；
  min(A,B) = Part A 0.79（binding）
- 驗收目標：min(A,B) > 4.08（CIBR 全域最優突破），維持 A/B 平衡。
  pre-analysis 預測不可達成（documented-failure，延伸 lesson #24 邊界）。
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR016Config(ExperimentConfig):
    """CIBR-016 ^VIX Implied-Vol Regime BANDS Filter MR 參數"""

    # === 進場框架（同 CIBR-008 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0
    pullback_lookback: int = 10
    pullback_cap: float = -0.12
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    # === ^VIX BANDS regime gate（CIBR-016 核心新增，XBI-017 跨資產移植）===
    # 訊號通過條件：VIX <= vix_low_threshold OR VIX > vix_high_threshold
    # Att2（post-hoc 嘗試 bracket 唯一 SL；SL VIX 25.03 ∈ (24.7, 25.4]）
    vix_ticker: str = "^VIX"
    vix_low_threshold: float = 24.7
    vix_high_threshold: float = 25.4
    use_vix_bands: bool = True

    cooldown_days: int = 8


def create_default_config() -> CIBR016Config:
    """建立預設配置（Att1：XBI-017 Att1 直接移植 vix_bands (17, 22)）"""
    return CIBR016Config(
        name="cibr_016_vix_bands_mr",
        experiment_id="CIBR-016",
        display_name="CIBR VIX Implied-Vol Regime BANDS Filter MR",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=18,
    )
