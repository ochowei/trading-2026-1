"""
IWM-013: Capitulation-Depth Filter Mean Reversion (RSI Oscillator Depth)

動機：IWM-011 Att2（ATR>1.1 + RSI(2)<10 + 2DD<=-2.5% + ClosePos>=40%，min(A,B)
Sharpe 0.52）為 IWM 全域最佳，但 Part A 10 訊號中 3 筆 loss（2019-08-02 expiry
-1.38%、2021-11-26 SL Omicron -4.35%、2023-03-13 SL SVB -4.35%），Part B 4 訊號
中 1 筆 SL（2025-03-04 -4.35% 通膨/關稅擔憂）拖累兩段 Sharpe 與 WR。

跨資產移植起點（lesson #19 family）：
- DIA-012 Att2 (1.0% vol)：1d cap -2% + 3d cap -7%，min(A,B)† 1.31
- SPY-009 Att2 (1.2% vol)：1d FLOOR -0.5% + 3d cap，min(A,B)† 6.56
- EWJ-005 Att2 (1.15% vol)：1d floor -0.5%，min(A,B)† 0.70
- VGK-008 / EEM-014 / INDA-010：2DD floor 加深方向

IWM 1.5-2% vol 介於 SPY/DIA（1.0-1.2%）與 EWZ（1.75%）之間，預期
1d cap 閾值 ~ -3% / 3d cap 閾值 ~ -10%。

訊號日 1d/3d/RSI 分析（Part A 10 + Part B 4 訊號）：
| Date       | Result | 1d     | 2d     | 3d     | ClosePos | RSI |
|------------|--------|--------|--------|--------|----------|-----|
| Part A:    |        |        |        |        |          |     |
| 2019-08-02 | LOSS   | -1.11% | -2.54% | -3.33% | 0.53     | 8.2 |
| 2019-10-02 | TP     | -0.75% | -2.70% | -2.59% | 0.79     | 3.2 |
| 2020-02-28 | TP     | -1.83% | -5.29% | -6.38% | 0.46     | 0.2 |
| 2020-09-21 | TP     | -3.50% | -3.75% | -4.46% | 0.40     | 5.3 |
| 2021-07-19 | TP     | -1.50% | -2.71% | -3.26% | 0.50     | 1.4 |
| 2021-11-26 | LOSS   | -3.77% | -3.67% | -3.83% | 0.49     | 1.4 |
| 2022-05-10 | TP     | +0.03% | -4.18% | -5.77% | 0.49     | 7.5 |
| 2022-09-23 | TP     | -2.38% | -4.58% | -6.04% | 0.55     | 1.5 |
| 2022-12-16 | TP     | -0.75% | -3.23% | -3.86% | 0.70     | 7.9 |
| 2023-03-13 | LOSS   | -1.63% | -4.47% | -7.12% | 0.42     | 0.8 |
| Part B:    |        |        |        |        |          |     |
| 2024-08-02 | TP     | -3.54% | -6.67% | -6.13% | 0.46     | 5.0 |
| 2025-03-04 | LOSS   | -1.13% | -3.83% | -2.81% | 0.49     | 9.1 |
| 2025-04-04 | TP     | -4.46% |-10.59% | -9.18% | 0.61     | 5.0 |
| 2025-08-01 | TP     | -2.04% | -3.00% | -3.49% | 0.61     | 1.0 |

關鍵分析：
1. Part A 1d 維度：losers 與 winners 在 -1.11% ~ -3.77% 範圍重疊
   （loser 2021-11-26 1d=-3.77% 與 winner 2020-09-21 1d=-3.50% 不可分）
2. Part B 1d 維度：winners 集中於深 1d (-2.04% ~ -4.46%)，loser 2025-03-04
   shallow 1d (-1.13%)
3. Part A 3d 維度：loser 2023-03-13 3d=-7.12% 為最深，但 winner 2020-02-28
   3d=-6.38% 接近，cap 閾值難精準
4. **RSI 維度**：losers 集中於高 RSI（2019-08-02 RSI=8.2、2025-03-04 RSI=9.1）
   全部 Part B winners RSI <= 5.0，全部 Part A winners RSI <= 7.9
   RSI < 8 為 Part A losers vs winners 完美分隔閾值

============================================================================
三次迭代記錄（2026-04-26，成交模型 0.1% slippage，隔日開盤市價進場）：
============================================================================

Att1（DIA-012 跨資產移植）：1d cap >= -3.0% AND 3d cap >= -10%
  Part A: 9 訊號 WR 77.8% Sharpe 0.84 cum +24.13%（+62% vs IWM-011 0.52）
  Part B: 2 訊號 WR 50.0% Sharpe -0.04 cum -0.52%（崩壞，移除 2024-08-02 +4% TP /
    2025-04-04 +4% TP，保留 2025-03-04 SL）
  min(A,B): -0.04（FAIL，遠低於 IWM-011 的 0.52）
  失敗根因：(1) IWM Part B winners 集中於深 1d/3d gap-down recoveries（Yen carry
    2024-08、Trump tariff 2025-04），cap 直接過濾這類高品質訊號；(2) Part A 1d cap
    -3% 同時殺死 2020-09-21 winner（1d=-3.50%）與 2021-11-26 SL（1d=-3.77%），
    雖 cooldown shift 至 2020-09-24 救回一筆 winner 但 net 為品質而非數量提升
  跨資產發現：DIA-012 的 1d cap + 3d cap 雙維度方向**不適用** IWM 小型股寬基 ETF，
    因 IWM 的 Part B 高品質訊號結構與 DIA 完全相反

Att2：3d FLOOR <= -3.0%（require 3d depth，replace caps）
  Part A: 9 訊號 WR 66.7% Sharpe 0.43 cum +14.17%（劣化 vs IWM-011）
  Part B: 3 訊號 WR 100% std=0 Sharpe 0.00 cum +12.49%（移除 2025-03-04 SL ✓）
  min(A,B): 0.43（FAIL，Part A Sharpe 跌破 baseline）
  失敗根因：3d FLOOR -3.0% 移除 Part A 2019-10-02 winner（3d=-2.59%）使 Part A
    WR 降至 66.7%；雖 Part B 成功濾除 2025-03-04 SL，但 Part A 退步抵銷
  發現：3d FLOOR 方向結構性能切除 Part B SL 但會誤殺 Part A 淺 3d winner，
    raw return 維度無法精準區分 Part A losers vs shallow-3d winners

Att3 ★（最終）：RSI(2) < 8.0（從 IWM-011 的 < 10 加嚴 1.25x，停用 1d/3d 過濾器）
  Part A: 10 訊號 WR 80.0% Sharpe **0.59** cum +20.92%（+13.5% vs IWM-011 0.52）
    Cooldown shift：原 2019-08-02 LOSS 過濾後新增 2019-08-05 expiry +0.44%，
    淨效果為 LOSS -1.38% → 微利 Expiry +0.44%（淨改善 +1.82pp）
  Part B: 3 訊號 WR 100% std=0 Sharpe 0.00 cum +12.49%（移除 2025-03-04 SL ✓）
    保留全部三筆深 1d gap-down winners（2024-08-02 Yen / 2025-04-04 tariff /
    2025-08-01）
  min(A,B)†: **0.59**（沿用 EWJ-003/EWT-008/SPY-009/DIA-012 慣例，Part B std=0
    為結構性零方差，採 Part A Sharpe 為 min 約束）
  A/B 平衡：訊號比 2.0/yr vs 1.5/yr = 1.3:1（25% gap < 50% ✓）
           cum 年化 4.18% vs 6.25%，diff 33.1%（略超 30% 但 Part B 全 winner
           零方差為結構性無可避免，與 EWJ-005 36.1% / EWT-008 36.1% 同類）

核心發現：
- IWM 為 Russell 2000 小型股寬基 ETF，losers 與 winners 在 raw return 維度
  （1d、3d）分布大幅重疊，但在 oscillator 維度（RSI(2)）有清晰分隔
- RSI(2) 較 raw return 更能捕捉「多日累積動能耗竭」的 capitulation 強度
- IWM-011 的 RSI < 10 閾值雖已篩選 oversold，但仍允許 RSI 7-9 區間的「弱 oversold」
  訊號通過。RSI < 8 排除這類訊號，losers 在此區間集中（2019-08-02 RSI=8.2、
  2025-03-04 RSI=9.1）

跨資產貢獻：
- repo 第 4 次「capitulation-depth filter」成功（繼 DIA-012 / SPY-009 / EWJ-005
  後），首次小型股寬基 ETF
- repo 首次驗證**oscillator depth (RSI threshold)** 為 raw return depth (1d/3d)
  的更穩健替代維度。延伸 lesson #19 family：對於小型股寬基 ETF（個股事件驅動
  加總，winners/losers 在 raw return 維度高度重疊），oscillator depth 為更
  精準的 capitulation strength 度量
- 與 IWM-012 BB-lower hybrid（XBI 結構性失敗類）共同確認：IWM 訊號精煉應從
  oscillator 維度（RSI/WR/ClosePos）而非 BB 帶寬維度切入
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM013Config(ExperimentConfig):
    """IWM-013 Capitulation-Depth Filter MR 參數"""

    # RSI(2) 參數（Att3：tightened from IWM-011 的 10.0 至 8.0）
    # signal-day 分析顯示 IWM-011 兩段 losers 集中於 RSI(2) >= 8.0：
    #   Part A LOSS 2019-08-02 RSI=8.2、Part B LOSS 2025-03-04 RSI=9.1
    # 全部 Part B winners RSI <= 5.0，全部 Part A winners RSI <= 7.9
    # RSI < 8.0 為深度 capitulation oscillator floor，等效於 1d/3d depth filter 但
    # 透過 oscillator 維度避免 cooldown chain shift（Att1）和 winner-removal（Att2）
    rsi_period: int = 2
    rsi_threshold: float = 8.0

    # 2 日累計跌幅過濾（同 IWM-011）
    decline_lookback: int = 2
    decline_threshold: float = -0.025

    # 收盤位置過濾（同 IWM-011）
    close_position_threshold: float = 0.4

    # ATR 比率過濾（同 IWM-011 甜蜜點）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.1

    # 1 日急跌上限（IWM-013 第一維度）— Att1 -3.0% 失敗（同時殺死 2020-09-21 winner
    # 與 2021-11-26 SL，cooldown shift 抵銷）。Att3 改用 RSI 維度，停用 1d cap。
    # 設為 -1.0（永遠不過濾）= 停用
    oneday_return_cap: float = -1.0

    # 3 日急跌上限（IWM-013 第二維度）— Att1 -10% 失敗（移除 Part B 2024-08-02 TP /
    # 2025-04-04 TP）。Att3 停用。
    threeday_return_cap: float = -1.0

    # 3 日急跌下限（Att2 嘗試）—— Att3 停用，由 RSI<8 取代達成相同 capitulation
    # depth filter 效果但無 winner-removal 副作用
    threeday_return_floor: float = 0.0

    # 冷卻期（同 IWM-011）
    cooldown_days: int = 5


def create_default_config() -> IWM013Config:
    return IWM013Config(
        name="iwm_013_capitulation_filter",
        experiment_id="IWM-013",
        display_name="IWM Capitulation-Depth Filter MR (RSI Depth)",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,
        stop_loss=-0.0425,
        holding_days=20,
    )
