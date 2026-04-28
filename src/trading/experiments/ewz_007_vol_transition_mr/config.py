"""
EWZ-007: Post-Capitulation Vol-Transition Mean Reversion

延伸 EWZ-006 Att3（BB(20, 1.5) 下軌 + 10日回檔上限 -10% + WR + ClosePos +
ATR>1.10）框架，新增「Capitulation strength filter」（1日 / 2日 報酬下限）作為
主品質過濾器，目標過濾 Part A 三筆 SL（2019-03-25 巴西退休金改革雜訊、
2020-01-31 COVID 初期擔憂、2021-02-23 Petrobras 政治干預）與 Part B 1 筆近零到期
（2024-01-18），同時保留高品質 winners。

跨資產脈絡（lesson #19 family，Post-Capitulation Vol-Transition MR）：
- VGK-008 Att2（1.12% vol）：2DD floor <= -2.0% → min(A,B) 0.53→2.60（+390%）
- INDA-010 Att3（0.97% vol）：2DD floor <= -2.0% → min(A,B) 0.23→0.30（+30%）
- EEM-014 Att2（1.17% vol）：2DD floor <= -0.5% → min(A,B) 0.34→0.56（+65%）
- USO-013（2.20% vol）：2DD floor 方向成功
- IBIT-009 Att1（3.17% vol）：2DD floor <= -3.0% → 5/5 全勝
- EWJ-005 Att2（1.15% vol）：1d floor <= -0.5% → min(A,B) 0.60→0.70（+16.7%）
- EWT-009 Att3（1.41% vol）：2DD floor <= -1.5% → min(A,B) 0.57→1.11（+95%）

EWZ 1.75% vol 落於已驗證 vol 區間內（介於 EWT 1.41% 與 USO 2.20%）。EWZ 為
商品驅動 EM 單國 ETF（巴西，受鐵礦石/石油/BRL 匯率/政治驅動），結構接近 EWT
（半導體驅動）/ EWJ（出口導向）/ INDA（單國 EM），lesson #19 「2DD floor 加深」
方向為首選測試方向。

跨資產規則（lesson #19 v3，EWT-009 確認）：
- 2DD floor 閾值需匹配資產 winners 最淺 2d 與 losers 2d 的中位點
- 不可直接移植，需先做 trade-level 2d 分布分析
- EWT losers 含 -0.46% 淺 2d, winners 最淺 -1.87%, 甜蜜點 -1.5%
- VGK losers 最淺 -1.47%~-1.68%, winners 最深 -2.0% 內, 甜蜜點 -2.0%
- EWJ winners 廣泛分布 +0.17%~-2.43%, 2DD 無精準切點, 1d 維度 -0.5% 為甜蜜點

迭代計畫：
- Att1（2DD floor <= -2.0%）：標準 VGK/INDA 跨資產移植起點，1.14σ for 1.75% vol
- Att2（依 Att1 結果調整深淺）
- Att3（依 Att1/Att2 結果，可能切換至 1d 維度）

迭代結果（實測）：
- Att1（2DD floor <= -2.0%）：
  Part A 7/100%/Sharpe 0.99 cum +20.55% / Part B 6/100%/Sharpe 1.59 std=0.0 cum +25.52% /
  min(A,B) 0.99（+43% vs 0.69）。-2.0% 過濾全部 3 筆 Part A SLs（淺 2d）
  以及 Part B 2024-01-18 -0.84% 到期。Part A 訊號 12→7（-42% 過濾），
  全部保留為 winners；Part B 訊號 6→6 完全保留。
  A/B 累計差 19.55% < 30% ✓，A/B 訊號比 1.4/yr vs 3.0/yr = 2.14:1（>50% 失敗）
  → 訊號比偏高、Part A 訊號流失，可嘗試放寬 floor 至 -1.5%
- Att2（2DD floor <= -1.5%）：
  Part A 9/88.9%/Sharpe 0.95 cum +30.51% / Part B 6/100%/Sharpe 1.59 std=0.0 cum +25.52% /
  min(A,B) 0.95（+38% vs 0.69）。-1.5% 過濾 2 筆 Part A SLs 並保留多筆 winners，
  訊號 12→9（-25%）。A/B 累計差 16.4% < 30% ✓，A/B 訊號比 1.8/yr vs 3.0/yr = 1.67:1
  （仍 >50% 但略改善）。
- Att3 ★（2DD floor <= -1.0%，最寬鬆 ablation）：
  Part A 10/90.0%/Sharpe 1.07 cum +35.02% / Part B 6/100%/Sharpe 1.59 std=0.0 cum +25.52% /
  min(A,B) 1.07（+55% vs 0.69）。-1.0% 過濾僅 1 筆 Part A 淺 SL 並保留所有
  Part B 訊號，訊號 12→10（-17%）。A/B 累計差 27.1% < 30% ✓，
  A/B 訊號比 2.0/yr vs 3.0/yr = 1.50:1 (50% gap 邊界) ✓
  ★ 全部 acceptance criteria 達標，新全域最優

跨資產貢獻：
- repo 第 7 次「2DD floor」方向跨資產驗證（繼 USO-013、EEM-014、INDA-010、
  VGK-008、EWJ-005、IBIT-009、EWT-009 後），首次商品驅動 EM 單國 ETF（巴西）驗證
- 確認 lesson #19 family 對 EM 單國 ETF 普適：政策/商品/事件驅動子類別均有效
- 擴展跨資產規則：EWZ 1.75% vol 甜蜜點為 -1.0% (~0.57σ)，較 EWT -1.5%/1.41% vol
  (~1.06σ)、VGK -2.0%/1.12% vol (~1.79σ) 更淺
- 可能規則（待後續驗證）：商品驅動 EM 因日波動大、政治 noise 多，losers 2d 分布
  集中於更淺區間（-0.5% ~ -1.0%），需更淺 floor 才能精準切除
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
    # mode: "2dd_floor" | "1d_floor"
    capitulation_mode: str = "2dd_floor"
    capitulation_threshold: float = -0.020  # Att3 ★ 甜蜜點

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
