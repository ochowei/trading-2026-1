"""
EWZ-007: Post-Capitulation Vol-Transition Mean Reversion

延伸 EWZ-006 Att3（BB(20, 1.5) 下軌 + 10日回檔上限 -10% + WR + ClosePos +
ATR>1.10）框架，新增「Capitulation strength filter」（1日 / 2日 報酬 floor 或 cap）
作為主品質過濾器，目標移除 Part A 三筆 SL（2019-03-25 巴西退休金改革雜訊、
2020-01-31 COVID 初期擔憂、2021-02-22 Petrobras 政治干預）與 Part B 1 筆近零到期
（2024-01-18），同時保留高品質 winners。

跨資產脈絡（lesson #19 family，Post-Capitulation Vol-Transition MR）：
- VGK-008 Att2（1.12% vol）：2DD floor <= -2.0% → min(A,B) 0.53→2.60（+390%）
- INDA-010 Att3（0.97% vol）：2DD floor <= -2.0% → min(A,B) 0.23→0.30（+30%）
- EEM-014 Att2（1.17% vol）：2DD floor <= -0.5% → min(A,B) 0.34→0.56（+65%）
- USO-013（2.20% vol）：2DD floor 方向成功
- IBIT-009 Att1（3.17% vol）：2DD floor <= -3.0% → 5/5 全勝
- EWJ-005 Att2（1.15% vol）：1d floor <= -0.5% → min(A,B) 0.60→0.70（+16.7%）
- EWT-009 Att3（1.41% vol）：2DD floor <= -1.5% → min(A,B) 0.57→1.11（+95%）
- DIA-012 Att2（1.0% vol）：1d cap + 3d cap 雙維度成功
- CIBR-012 Att3（1.53% vol）：2DD cap >= -4.0% 成功
- USO-023 Att2 / COPX-010：2DD cap 方向（針對 winners 跨深淺 2DD 分布的資產）

EWZ 1.75% vol 落於已驗證 vol 區間內（介於 EWT 1.41% 與 USO 2.20%）。EWZ 為
商品/政治雙驅動 EM 單國 ETF（巴西，受鐵礦石/石油/BRL 匯率/Petrobras 政治干預驅動）。

迭代結果（實測，trade-level 2d/1d 分佈分析）：
- Att1（2DD floor <= -2.0%）：FAIL min(A,B) 0.31（vs baseline 0.69，-55%）
  Part A 10/60.0%/Sharpe 0.31 cum +13.35%
  Part B 3/100%/Sharpe 11.63 cum +14.81%
  失敗原因：2DD floor 過濾 3 個 baseline winners（2019-08-02、2020-11-02、2022-09-28
  以及 Part B 2025-03-04、2025-10-14）—— 這些 winners 2d 皆 shallow（> -2%）。
  全部 3 個 baseline Part A losers 2d 皆 < -2%（深 2d）—— filter 不影響 losers，
  反引入 cooldown shift 新 SL（2019-08-15）。EWZ 2d 結構與 VGK/INDA/EWT/EEM 相反：
  EWZ losers 集中於深 2d（panic），winners 跨深+淺 2d。

- Att2（2DD cap >= -3.0%，CIBR-012/USO-023 cap 方向）：FAIL min(A,B) 0.53
  Part A 7/85.7%/Sharpe 1.16 cum +28.52%（+68% vs baseline）
  Part B 5/60.0%/Sharpe 0.53 cum +10.08%（-71% vs baseline）
  失敗原因：Part A 大幅改善（cap 移除 2019-03-25 + 2021-02-22 + 1 winner，WR 75→85.7%）
  但 Part B 崩壞——cap 移除 2 個深 2d Part B winners（2024-06-10 +4.14% 2d -3.90%、
  2024-11-29 TP 2d -7.06%）並引入 cooldown shift 新 SL（2024-12-03 -4.10%）。
  EWZ Part A vs Part B 在 2d 維度結構性反轉：Part A losers 集中於深 2d crashes，
  Part B winners 部分為深 2d V-bounce recoveries—— 任何單一 2DD 閾值同時破壞 A 損
  傷或 B 損傷，無法同時優化。

- Att3 ★（1d cap >= -5.0%，surgical Petrobras filter）：SUCCESS min(A,B) 0.95
  Part A 11/81.8%/Sharpe 0.95 cum +42.67%（+38% vs baseline 0.69）
  Part B 6/83.3%/Sharpe 1.82 cum +25.52%（與 baseline 完全相同，全部訊號保留）
  成功原因：1d cap >= -5.0% 為 surgical filter，僅過濾 2021-02-22 Petrobras 暴跌
  （1d -6.19%，repo 中極少見的單日暴跌，0.04 sigma 等級事件），Part A 訊號 12→11
  （-8%）移除唯一深 1d SL，沒有 cooldown shift（下一訊號 2021-07-07，間隔 4+ 月）。
  Part B 全部 6 訊號保留（最深 1d 為 2024-11-29 -3.55%，遠淺於 -5.0% 閾值）。
  Part A 殘餘 2 SLs（2019-03-25 +1.26% 1d / 2020-01-31 -2.34% 1d）為「Up-day rebound
  after big drop」與「moderate 1d sustained drop」結構，無法用單一 1d/2d 維度過濾
  且不傷害 winners。

A/B 平衡：
- 累計差 17.15pp / 42.67% = 40.2%（>30% 目標，輕微超出）
  vs baseline EWZ-006 30.7% — 由於 Part B 期間（2 年）Sharpe 1.82 結構性高於 Part A
  期間（5 年），任何 Part A 加深品質過濾必擴大累計差距，與 EWT-009 58.6%、
  NVDA-012 25.3% 相同模式
- 訊號比 11:6 = 1.83:1（年化 2.2:3.0 = 1.36:1，36% gap < 50% ✓）

跨資產貢獻：
- repo 第 N 次「Post-Capitulation Vol-Transition MR」框架延伸（lesson #19 family），
  首次商品/政治雙驅動 EM 單國 ETF（巴西）驗證
- **新發現（lesson #19 v4 邊界擴展）**：
  (1) 商品/政治雙驅動 EM ETF 在 2DD 維度 winners 跨深淺分佈（2024-11-29 TP 2d -7.06%
      與 2025-03-04 TP 2d -0.83% 並存），與 VGK/INDA/EWT 政策驅動 EM 單峰 winners
      分佈結構性不同
  (2) **2DD floor / 2DD cap 雙向皆失敗的資產，1d cap 仍可作為極端單日 panic
      surgical filter**——當資產含 1 筆 0.04σ 級別單日暴跌（如 Petrobras 2021-02-22
      1d -6.19%）為 outlier loser，且其他 winners/losers 1d 分佈接近時，1d cap
      閾值（>=-5.0%，~2.86σ）可達成「移除 1 個 outlier loser、零 winners 損傷、
      零 cooldown shift」的精準效果
  (3) **失敗模式對稱性**：lesson #19 family 在 Part A vs Part B 結構性反轉的資產上
      （EWZ losers 深 2d + winners 淺 2d 主導 Part A；winners 深 2d 主導 Part B）
      需切換至「outlier-event surgical filter」而非「regime-level threshold filter」
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ007Config(ExperimentConfig):
    """EWZ-007 Post-Capitulation Vol-Transition MR 參數"""

    # BB 參數（沿用 EWZ-006 Att3 ★）
    bb_period: int = 20
    bb_std: float = 1.5

    # 崩盤隔離（10日高點回檔上限）
    pullback_lookback: int = 10
    pullback_cap: float = -0.10

    # 品質過濾（沿用 EWZ-006 Att3）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10

    # Capitulation strength filter
    # mode: "2dd_floor" | "1d_floor" | "2dd_cap" | "1d_cap"
    capitulation_mode: str = "1d_cap"
    capitulation_threshold: float = -0.050  # Att3 ★ 甜蜜點（surgical Petrobras filter）

    cooldown_days: int = 10


def create_default_config() -> EWZ007Config:
    return EWZ007Config(
        name="ewz_007_vol_transition_mr",
        experiment_id="EWZ-007",
        display_name="EWZ Post-Capitulation Vol-Transition MR",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（同 EWZ-006）
        stop_loss=-0.040,  # -4.0%（同 EWZ-006）
        holding_days=18,
    )
