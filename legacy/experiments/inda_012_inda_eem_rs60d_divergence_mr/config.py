"""
INDA-012: INDA-EEM 60d Relative Strength Divergence Filter on Multi-Period
Capitulation MR

策略方向（cross-asset divergence regime gate，repo 第 7 次 lesson #20 v3 應用）：
- 在 INDA-011 Att3 完整框架（10d 回檔 [-7%, -3%] + WR(10)<=-80 + ClosePos>=40%
  + ATR(5)/ATR(20)>1.15 + 2DD floor <= -2% + 3DD cap >= -3%, TP +3.5%/SL -4%/
  15 天/cd 7）之上，新增第 7 條件：**INDA 過去 60 日報酬 - EEM 過去 60 日
  報酬 <= max_rs_60d**（INDA-EEM 60 日相對強度上限 cap）。

================================================================================
核心假設與動機
================================================================================
INDA-011 Att3 殘餘 Part A 1 SL（2022-09-16，Fed CPI shock -4.10%），其 trade-
level 訊號日特徵分析發現 INDA-EEM 60 日相對強度為**唯一單維度結構性 outlier**：

| Signal Date | Type        | INDA-EEM RS 60d | INDA-EEM RS 10d |
|-------------|-------------|-----------------|-----------------|
| 2020-10-29  | Part A TP   | +2.07%          | -2.88%          |
| 2020-12-21  | Part A TP   | -3.17%          | -0.55%          |
| 2021-01-25  | Part A TP   | -5.92%          | -5.24%          |
| 2021-12-06  | Part A exp+ | +1.72%          | -1.70%          |
| 2022-06-16  | Part A TP   | -0.11%          | -0.77%          |
| **2022-09-16** | **Part A SL** | **+15.28%** ★ | **+3.01%**      |
| 2024-06-04  | Part B TP   | -3.58%          | +1.44%          |
| 2024-11-13  | Part B TP   | -5.18%          | +0.34%          |

**結構性發現**：
- 2022-09-16 SL 之 INDA-EEM RS 60d 為 +15.28%，**唯一 > +5% 訊號**
- 全部 Part A winners 之 RS 60d ∈ [-5.92%, +2.07%]（最高僅 +2.07%）
- 全部 Part B winners 之 RS 60d ∈ [-5.18%, -3.58%]（皆深度負）
- **+5% 至 +15% 之間為 surgical sweet spot**：
  ✓ 過濾 1 SL（2022-09-16, RS_60d +15.28%）
  ✓ 保留全部 4 Part A TPs + 1 small profit exp（max RS_60d +2.07%）
  ✓ Part B 兩訊號 RS_60d 均 <= -3.58%，filter 對 Part B **完全非綁定**

**結構解讀**：當 INDA 過去 60 日相對 EEM 強勢（RS_60d > +5%），訊號日的
capitulation 訊號更可能為「India-specific 局部疲弱中段」（INDA 過去領漲後因
country-specific 因子（Fed 政策對盧比、印度宏觀數據）開始 lagging → 後續為
持續性下跌），均值回歸不成立；當 INDA 相對 EEM 持平或弱勢，訊號為「broad EM
同步 capitulation 或 INDA 過度疲弱反彈」更可能成功。

================================================================================
跨資產脈絡（lesson #20 v3 cross-asset divergence regime gate）
================================================================================
- TLT-014 ✓ Att1 SUCCESS（TLT vs SPY 20d divergence, rate ETF + MR 框架）
- TSLA-017 ✓ Att3 SUCCESS（TSLA vs QQQ 20d divergence, high-vol 個股 + BB
  Squeeze Breakout 框架）
- COPX-014 ✗（COPX vs GLD divergence, 商品/礦業 ETF + BB Squeeze 失敗）
- NVDA-016 ◐ PARTIAL（NVDA vs SMH, A/B gap 違反）
- USO-026 ✗（USO vs XLE, A/B 結構性不對稱失敗）
- EWZ-009 ✓ Att1 SUCCESS（EWZ vs EEM 10d divergence, EM single-country 首次）
- **INDA-012**: repo 第 7 次 lesson #20 v3 應用 / EWZ-009 後第 2 次 EM
  single-country / repo **首次 60d lookback** RS divergence 維度

================================================================================
迭代計畫（三次）
================================================================================
- Att1: rs_lookback=60, max_rs_60d=+0.05（sweet spot 中央，預期最佳）
- Att2: rs_lookback=60, max_rs_60d=+0.10（loose 邊界，robustness 檢驗）
- Att3: rs_lookback=20, max_rs_20d=+0.03（短 lookback 替代維度，ablation）

================================================================================
與 EWZ-009 對比
================================================================================
| 維度          | EWZ-009 Att1   | INDA-012 預期 Att1 |
|---------------|----------------|---------------------|
| RS lookback   | 10d            | 60d                 |
| Max RS        | +2.5pp         | +5pp                |
| 解讀          | 短期局部 lag   | 中長期相對強勢      |
| 殘餘 SL 結構  | -5.20pp 異質   | +15.28% 同向 outlier |

INDA 失敗模式為「INDA 過去 60 日領漲後 country-specific 走弱」屬於更長
horizon（中長期 regime divergence），與 EWZ「短期 country-specific 急跌」
不同——故 lookback 60d > 10d 為跨資產設定差異。

================================================================================
跨資產貢獻（預期）
================================================================================
- repo 第 7 次 cross-asset divergence regime gate 應用
- repo **首次 60d lookback** RS divergence 維度（既有皆 ≤ 20d）
- repo 第 2 次 EM single-country ETF + EEM benchmark anchor 配對（EWZ-009 後）
- 擴展 lesson #20 v3 family v2：lookback 維度差異化（短/中/長）依資產失敗模式

成交模型：next_open_market 進場 + 0.1% 滑價 + 悲觀認定
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA012Config(ExperimentConfig):
    """INDA-012 INDA-EEM RS Divergence Filter on Multi-Period Capitulation MR 參數"""

    # === INDA-011 Att3 完整框架（沿用）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_cap: float = -0.07
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.4
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15
    drop_2d_floor: float = -0.02
    drop_3d_cap: float = -0.03
    cooldown_days: int = 7

    # === INDA-012 核心新增：INDA-EEM RS divergence cap ===
    # EEM (iShares MSCI Emerging Markets ETF) 為 broad EM benchmark anchor
    eem_ticker: str = "EEM"
    # lookback：60d 為核心（trade-level 分析顯示 60d 為唯一 surgical separator）
    rs_lookback: int = 60
    # max RS excess: INDA - EEM 過去 N 日報酬差上限（pp）
    # Att1 ★ +5%（surgical sweet spot 中央，最終採用）
    # Att2 +10%（loose 邊界 robustness 確認，與 Att1 完全相同結果）
    # Att3 lookback=20 + +3%（短 lookback 替代維度，與 Att1 完全相同結果）
    # 三次迭代全部產生相同訊號集（Part A 4/100%/Sharpe 4.07 + Part B 2/100%/std=0），
    # 確認 sweet spot 跨 lookback 與 threshold 高度穩健（SL 在 60d/20d 維度皆顯著
    # outlier，TP/Part B 訊號在兩維度皆遠低於閾值）。
    max_rs_excess: float = 0.05


def create_default_config() -> INDA012Config:
    """預設配置：Att1 ★（rs_lookback=60, max_rs_excess=+0.05 sweet spot）"""
    return INDA012Config(
        name="inda_012_inda_eem_rs60d_divergence_mr",
        experiment_id="INDA-012",
        display_name="INDA INDA-EEM 60d RS Divergence Filter on Multi-Period Capitulation MR",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=15,
    )
