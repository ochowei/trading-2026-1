"""
EWT-010: EWT-EEM 2D Cross-Asset Divergence Filter on Vol-Transition MR

策略方向（cross-asset divergence regime gate，repo 第 N 次 lesson #20 v3 應用）：
- 在 EWT-009 Att3 完整框架（BB(20,2.0) 下軌 + 10d 回檔上限 -8% + WR(10)<=-80
  + ClosePos>=40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -1.5%, TP+3.5%/SL-4%/
  20 天/cd 10）之上，新增第 7 條件：**EWT-EEM 雙時框 (5d AND 60d) 相對強度
  divergence 過濾**——當 EWT 同時於短時框（5d）顯著強過 EEM AND 中期（60d）
  維持結構性領先，訊號被過濾。

================================================================================
核心假設與動機
================================================================================
EWT-009 Att3 殘餘 Part A 1 SL（2019-05-09 中美貿易戰升級 -4.10%）。Trade-level
分析發現 EWT-EEM 單一 lookback（5d/10d/20d/60d）皆**無法**單獨區分 SL 與 TPs：

| Date        | Out  | 5d div | 10d div | 20d div | 60d div |
|-------------|------|--------|---------|---------|---------|
| 2019-05-09  | SL   | +1.64  | +1.71   | +4.35   | +7.37   |
| 2019-08-02  | TP   | +0.31  | +0.83   | +3.03   | -0.23   |
| 2020-01-27  | TP   | +1.32  | +1.02   | -0.45   | +0.98   |
| 2020-09-24  | TP   | -0.52  | -1.02   | +0.79   | +0.13   |
| 2021-07-27  | TP   | +2.42  | +2.65   | +6.51   | +2.70   |
| 2021-08-17  | TP   | -1.45  | -2.35   | -0.08   | +7.26   |
| 2022-01-28  | TP   | +0.55  | -1.66   | -2.31   | +7.46   |
| 2023-03-15  | TP   | +0.20  | +1.89   | +2.87   | +5.97   |
| 2023-07-06  | TP   | -1.11  | -1.55   | -1.14   | +2.76   |
| 2024-04-16  | TP-B | -1.54  | -1.15   | -1.03   | +1.89   |
| 2025-01-13  | TP-B | -0.57  | -0.53   | +1.48   | +3.25   |
| 2025-11-18  | TP-B | -1.41  | -3.14   | -4.23   | -1.60   |

**單一 lookback 結構性失敗**：
- 5d <= +1.5pp 過濾 SL (+1.64) 但同時過濾 2021-07-27 TP (+2.42)
- 10d <= +1.7pp 過濾 SL (+1.71) 但同時過濾 2021-07-27 TP (+2.65)、2023-03-15 TP (+1.89)
- 20d <= +4.3pp 過濾 SL (+4.35) 但同時過濾 2021-07-27 TP (+6.51)
- 60d <= +7.40pp 過濾 SL (+7.37) 但同時過濾 2022-01-28 TP (+7.46)

**雙時框 surgical separator**：(short_div >= short_thresh) **AND** (long_div >=
long_thresh) 同時成立時過濾。SL 在 5d (+1.64) AND 60d (+7.37) 兩維度同時越過閾
值，winners 任一維度低於閾值。

================================================================================
跨資產脈絡（lesson #20 v3 cross-asset divergence regime gate）
================================================================================
- TLT-014 ✓ Att1 SUCCESS（TLT-SPY 20d, rate ETF + MR）
- TSLA-017 ✓ Att3 SUCCESS（TSLA-QQQ 20d, 高 vol 個股 + BB Squeeze Breakout）
- COPX-014 ✗（COPX-GLD divergence, 商品/礦業 ETF + BB Squeeze 失敗）
- NVDA-016 ◐ PARTIAL（NVDA-SMH, A/B gap 違反）
- USO-026 ✗（USO-XLE, A/B 結構性不對稱失敗）
- EWZ-009 ✓ Att1 SUCCESS（EWZ-EEM 10d, EM single-country 首次）
- INDA-012 ✓ Att1 SUCCESS（INDA-EEM 60d, 第 2 次 EM single-country, 60d 首次）
- EWJ-006 ✓ Att2 SUCCESS（EWJ-USDJPY 10d, 首次 bilateral FX direction）
- FXI-015 ✓ Att2 SUCCESS（FXI-ASHR 20d, 首次 H-share/A-share intra-China）
- GLD-016 ✓ Att1 SUCCESS（GLD-DXY, 首次商品 safe-haven + FX axis）
- **EWT-010**: repo 第 11 次 lesson #20 v3 應用 / 第 3 次 EM single-country
  + EEM anchor（EWZ-009 / INDA-012 後）/ **repo 首次「雙時框 (5d AND 60d) 同時
  AND 條件」divergence 過濾器於任何資產**

================================================================================
迭代結果（三次）
================================================================================
- Att1（5d/+1.5pp AND 60d/+5pp）: cooldown chain-shift FAIL（TIE baseline 1.11）
  Part A 9/88.9%/Sharpe **1.11** cum +26.28%（與 baseline 完全相同數字）/ Part B 3/100%/std=0 cum +10.87% / min(A,B)† **1.11** TIE
  原因：5d_div +0.43pp 為 2019-05-13（原本被 cooldown 壓制的下一個訊號）的 5d
  divergence，未越過 +1.5pp 閾值；2019-05-09 SL 過濾後 cooldown 解除 → 2019-05-13
  以新 SL (-4.10%) 啟動。lesson #19 family cooldown chain-shift 失敗模式。

- Att2 ★（20d/+3.0pp AND 60d/+5pp）: **SUCCESS — repo 第 11 次 lesson #20 v3
  cross-asset divergence regime gate 應用，repo 首次「雙時框 AND 條件」divergence
  過濾於任何資產**
  Part A **8/100% WR/std=0** cum **+31.68%** MDD -3.89% （vs baseline 9/88.9%/
  1.11/+26.28%/-4.08%）/ Part B 3/100%/std=0 cum +10.87% 不變 / min(A,B)†
  **structurally NO LOSS**（雙 Part 全勝零方差，依 IBIT-009 Att1 慣例優於
  baseline 1.11/std=0 的「Part A 1 SL + Part B 全勝」結構）
  20d 維度同時切除 2019-05-09 SL（20d +4.35）與 cooldown chain-shift 2019-05-13
  SL（20d +3.37），所有 11 個 TPs 保留（最近邊界 2019-08-02 TP 20d +3.03，但 60d
  -0.23 < +5 由 AND 條件保護）。
  A/B 年化 cum 6.34%/y vs 5.43%/y → gap **14.4% < 30% ✓**（vs baseline 11.8%
  microscopic diff — 結構性同等，但 Sharpe 升級為「全勝零方差」）
  A/B 訊號比 1.6:1.5 = **6.7% gap << 50% ✓**（vs baseline 16.7%，進一步改善）

- Att3（20d/+2.5pp AND 60d/+5pp loose threshold robustness）:
  Part A **7**/100%/std=0 cum +27.23% / Part B 3/100%/std=0 cum +10.87% /
  min(A,B)† structurally NO LOSS but Part A cum **下降** vs Att2
  +2.5pp 過鬆同時過濾 2023-03-15 TP（20d +2.87 ≥ 2.5 ✓ AND 60d +5.97 ≥ 5 ✓）
  → 確認 +3.0pp 為 short_threshold 結構性下界 sweet spot

================================================================================
與 EWZ-009 / INDA-012 / EWJ-006 對比
================================================================================
| 維度          | EWZ-009 Att1 | INDA-012 Att1 | EWJ-006 Att2 | EWT-010 Att2 ★ |
|---------------|--------------|---------------|--------------|----------------|
| Anchor        | EEM          | EEM           | USDJPY       | EEM            |
| Lookback      | 10d          | 60d           | 10d          | 20d AND 60d    |
| Threshold     | +2.5pp       | +5pp          | +1.0%        | +3.0pp/+5pp    |
| Filter dim    | 1D           | 1D            | 1D           | **2D AND**     |

EWT 失敗模式特殊：SL 在任一單一 lookback 上**非 outlier**（與 INDA-012
2022-09-16 SL 之 60d +15.28% 為唯一 > +5% outlier 不同），需雙時框 AND 條件
才能 surgical separation。**lesson #20 v3 family v3：dimensionality 從 1D 擴展
至 2D AND，依資產失敗模式選擇**。

================================================================================
跨資產貢獻（預期）
================================================================================
- repo 第 11 次 cross-asset divergence regime gate 應用
- repo **首次「雙時框 5d AND 60d 同時 AND 條件」divergence 過濾器於任何資產**
- repo 第 3 次 EM single-country + EEM benchmark anchor（EWZ-009 / INDA-012 後）
- 首次半導體驅動 EM single-country ETF（EWT 1.41% vol，TSM ~25% 權重）+ EEM
  anchor + 雙時框 AND 條件
- 擴展 lesson #20 v3 family v3：dimensionality（1D → 2D AND）依失敗模式選擇

成交模型：next_open_market 進場 + 0.1% 滑價 + 悲觀認定
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT010Config(ExperimentConfig):
    """EWT-010 EWT-EEM 2D Divergence Filter on Vol-Transition MR 參數"""

    # === EWT-009 Att3 完整框架（沿用） ===
    bb_period: int = 20
    bb_std: float = 2.0
    pullback_lookback: int = 10
    pullback_cap: float = -0.08
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10
    capitulation_mode: str = "2dd_floor"
    capitulation_threshold: float = -0.015
    cooldown_days: int = 10

    # === EWT-010 核心新增：EWT-EEM 雙時框 divergence 過濾 ===
    # EEM (iShares MSCI Emerging Markets ETF) 為 broad EM benchmark anchor
    eem_ticker: str = "EEM"
    # 雙時框 lookback（短期 + 中期）
    rs_short_lookback: int = 20
    rs_long_lookback: int = 60
    # 雙時框閾值（兩條件同時成立才過濾訊號）
    # Att1 short_lb=5, short=+0.015, long=+0.05 — chain-shift TIE baseline 1.11
    # Att2 ★ short_lb=20, short=+0.030, long=+0.05（surgical sweet spot，雙 SL
    #        同時切除，雙 Part 全勝零方差，min(A,B)† structurally NO LOSS）
    # Att3 short_lb=20, short=+0.025, long=+0.05（過鬆，loses 2023-03-15 TP）
    rs_short_threshold: float = 0.030
    rs_long_threshold: float = 0.05


def create_default_config() -> EWT010Config:
    """預設配置：Att1 ★（5d/+1.5pp AND 60d/+5pp surgical sweet spot）"""
    return EWT010Config(
        name="ewt_010_ewt_eem_2d_divergence_mr",
        experiment_id="EWT-010",
        display_name="EWT EWT-EEM 2D Divergence Filter on Vol-Transition MR",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.040,
        holding_days=20,
    )
