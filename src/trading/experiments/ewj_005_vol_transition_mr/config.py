"""
EWJ-005: Post-Capitulation Vol-Transition Mean Reversion

延伸 EWJ-003 Att3（BB(20,1.5) 下軌 + 10日回檔上限 7% + WR + ClosePos + ATR>1.15）
框架，新增「2 日報酬下限」（2DD floor）作為主品質過濾器，目標過濾 Part A 兩筆
SL（2022-09-01 BoJ pivot + 2023-08-03 yield surge），同時保留高品質 winners。

跨資產脈絡（lesson #19 family）：
- VGK-008 Att2（1.12% vol）：2DD floor <= -2.0% → min(A,B) 0.53→2.60（+390%）
- INDA-010 Att3（0.97% vol）：2DD floor <= -2.0% → min(A,B) 0.23→0.30
- EEM-014（1.17% vol）：2DD floor 方向成功
- USO-013（2.20% vol）：2DD floor 方向成功
- DIA-012（1.0% vol）：1d cap + 3d cap 方向成功（不同方向但同 family）
- SPY-009（1.0% vol）：1d floor 方向成功

EWJ 1.15% vol 落在 lesson #19 已驗證 vol 區間內。Part A 兩筆 SL 的 2DD 為
-1.63%（2022-09-01）與 -2.36%（2023-08-03），floor 過濾邏輯：require 2DD <=
-2.0% 過濾「淺 2DD drift」訊號（包含 2022-09-01 SL）；保留「深 2DD capitulation」
訊號（含 2023-08-03 SL，但伴隨多筆 winners）。

迭代結果：
- Att1（2DD floor <= -2.0%，VGK-008 Att2 直接移植）：Part A 7/85.7%/0.61
  cum +11.06% / Part B 3/100%/std=0 cum +10.87% / min(A,B)† 0.61（+1.7% vs
  baseline 0.60，邊際）。EWJ Part A 兩筆 SL 的 2DD 為 -1.63%（過濾）/-2.36%
  （保留），且 winners 2DD 廣泛分佈 +0.17% ~ -2.43%，2DD floor 同時切除多筆
  shallow-2DD winners（6 筆）以換取 1 筆 SL，淨效果有限。
- Att2 ★（1d floor <= -0.5%，SPY-009 方向）：Part A 9/88.9%/Sharpe **0.70**
  cum +14.72% / Part B 4/100%/std=0 cum +14.75% / min(A,B)† **0.70**（+16.7%
  vs baseline，A/B 累計差 0.03pp 近乎完美平衡）。1d 維度成功過濾 2023-08-03
  SL（1d -0.49% > -0.5% 邊界，恰好被排除）並保留所有深 1d 高品質訊號；副作用
  為過濾 3 筆 1d 過淺贏家（2021-08-20 +0.08%、2021-10-05 +0.56%、2022-01-28
  +0.38%），總體 Sharpe 上升。
- Att3（1d floor <= -0.7%，加嚴測試）：Part A 6/83.3%/0.46 cum +7.11% / Part
  B 3/100%/std=0 cum +10.87% / min(A,B)† 0.46（-23% vs Att2）。-0.7% 移除 3
  筆淺 1d 贏家（2019-05-08 -0.61%/+2.23%、2019-08-02 -0.52%/+1.22%、
  2020-10-30 -0.58%/+3.50%）使 Part A 訊號從 9 縮至 6，確認 -0.5% 為甜蜜點。

跨資產貢獻：repo 第 2 次「1d floor」方向成功驗證（繼 SPY-009 後），首次
非美 ETF 驗證；擴展 lesson #19 至 EWJ 1.15% vol 已開發亞洲寬基。失敗模式
分析：EWJ Part A SLs 集中於「淺 1d drift + BB 下軌假觸碰」結構（2022-09-01
1d -1.19% 通過、2023-08-03 1d -0.49% 被過濾），與 SPY 同類失敗結構。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWJ005Config(ExperimentConfig):
    """EWJ-005 Post-Capitulation Vol-Transition MR 參數"""

    # BB 參數（沿用 EWJ-003 Att3）
    bb_period: int = 20
    bb_std: float = 1.5

    # 崩盤隔離（10日高點回檔上限）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    # 品質過濾（沿用 EWJ-003 Att3）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    # 新增：Capitulation strength filter
    # mode: "2dd_floor" | "1d_floor"
    capitulation_mode: str = "2dd_floor"
    # 對應閾值（負數，要求 N 日報酬 <= 此值才通過）
    capitulation_threshold: float = -0.02

    cooldown_days: int = 7


def create_default_config() -> EWJ005Config:
    return EWJ005Config(
        name="ewj_005_vol_transition_mr",
        experiment_id="EWJ-005",
        display_name="EWJ Post-Capitulation Vol-Transition MR",
        tickers=["EWJ"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 EWJ-003）
        stop_loss=-0.040,  # -4.0%（同 EWJ-003）
        holding_days=20,
    )
