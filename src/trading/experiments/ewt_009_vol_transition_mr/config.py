"""
EWT-009: Post-Capitulation Vol-Transition Mean Reversion

延伸 EWT-008 Att1（BB(20, 2.0) 下軌 + 10日回檔上限 -8% + WR + ClosePos + ATR>1.10）
框架，新增「Capitulation strength filter」（1日 或 2日 報酬下限）作為主品質過濾器，
目標過濾 Part A 兩筆 SL（2019-05-09 中美貿易戰升級 + 2022-01-25 科技股拋售/Fed pivot
擔憂），同時保留高品質 winners。

跨資產脈絡（lesson #19 family）：
- VGK-008 Att2（1.12% vol）：2DD floor <= -2.0% → min(A,B) 0.53→2.60（+390%）
- INDA-010 Att3（0.97% vol）：2DD floor <= -2.0% → min(A,B) 0.23→0.30
- EEM-014（1.17% vol）：2DD floor 方向成功
- USO-013（2.20% vol）：2DD floor 方向成功
- DIA-012（1.0% vol）：1d cap + 3d cap 雙維度 方向成功
- SPY-009（1.0% vol）：1d floor 方向成功
- EWJ-005 Att2（1.15% vol）：1d floor <= -0.5% → min(A,B) 0.60→0.70（+16.7%）

EWT 1.41% vol 落在 lesson #19 已驗證 vol 區間內（含 EEM 1.17%、EWJ 1.15%、INDA 0.97%、
EWZ 1.75%）。半導體驅動單一國家 EM ETF 結構接近 EWJ（DM 已開發但同樣亞洲 export-led），
1d floor 為首選測試方向。

迭代結果：
- Att1（2DD floor <= -2.0%，VGK-008 Att2 / EEM-014 / INDA-010 / EWJ-005 Att1 直接移植）：
  Part A 7/85.7%/Sharpe 0.91 cum +17.89% / Part B 3/100%/std=0 cum +10.87% /
  min(A,B)† 0.91（+59.6% vs baseline 0.57）。-2.0% 過嚴：2019-05-09（2d -1.69%）
  + 2023-03-15（2d -1.87%）winners 兩筆被同時過濾，且因 2019-05-09 移除引入
  2019-05-13 cooldown shift 新 SL（lesson #19）。Sharpe 大幅改善但 Part A 訊號
  從 9 縮至 7，A/B 訊號比惡化至 7:3 = 2.33:1。
- Att2（1d floor <= -1.0%，SPY-009 / EWJ-005 Att2 1d 維度跨資產移植）：
  Part A 8/87.5%/Sharpe 1.01 cum +22.01% / Part B **2**/100%/std=0 cum +7.12% /
  min(A,B)† 1.01（+77% vs baseline）。1d 維度精準過濾 2022-01-25 SL（1d -0.95%）
  但**同時誤殺 Part B 2025-11-18 winner**（1d -0.78% 落於 -1.0% 邊界外），Part B
  從 3 縮至 2，cum +10.87%→+7.12%。Sharpe 升至 1.01 但 Part B 訊號流失為主要副作
  用，總體不如 Att3。
- Att3 ★（2DD floor <= -1.5%，精準目標 2022-01-25 SL 之 2d -0.46%）：
  Part A 9/88.9%/Sharpe **1.11** cum +26.28% / Part B 3/100%/std=0 cum +10.87% /
  min(A,B)† **1.11**（+94.7% vs baseline 0.57）。-1.5% 為 2022-01-25 SL（2d
  -0.46%）與其餘所有 winners（最淺 2d -1.69% = 2019-05-09，仍 SL）/ 2021-07-27
  TP（2d -2.15%）的精準切點。**意外收益（cooldown chain shift 正向）**：移除
  2022-01-25 SL 後，原本被 cooldown 抑制的 2022-01-28 訊號活化並達標 +3.50%，
  Part A 訊號數**保持 9 不變**，但 8 TPs + 1 SL = 88.9% WR（vs baseline 7 TPs +
  2 SLs = 77.8%）。Part B 全部 3 筆 winners 保留（2d -3.70%/-4.23%/-3.84% 皆深
  於 -1.5%）。

跨資產貢獻：repo 第 N 次「2DD floor」方向成功驗證（繼 USO-013、EEM-014、INDA-010、
VGK-008、EWJ-005 後），首次 EM 半導體驅動單一國家 ETF 驗證。失敗模式分析：EWT Part A
SLs 在 2d 維度具區分力（2022-01-25 2d -0.46% 過淺、2019-05-09 2d -1.69% 較深但仍
SL），2DD floor -1.5% 精準切除淺 2d drift winners。EWT 2DD 維度有效（不同於 EWJ-005
Att1 的 2DD -2.0% 過嚴），因 EWT 有 1 筆淺 2DD SL（-0.46%）剛好被 -1.5% 過濾，且
所有 winners 2d 皆深於 -1.5%（最淺 -1.87% = 2023-03-15 TP）。

A/B 平衡：
- 累計差 15.41pp / 26.28% = 58.6%（>30% 目標）— 仍超 30% 但保持與 baseline EWT-008
  的 36.1% 同數量級；Part B std=0 結構性限制使 Sharpe 提升必伴隨 Part A 累計擴張
- 訊號比 9:3 = 3:1（gap 66.7%）— 與 baseline EWT-008 9:3 完全相同
- Sharpe 大幅 +95% 為主要績效改善，A/B 平衡維持 baseline 水平
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT009Config(ExperimentConfig):
    """EWT-009 Post-Capitulation Vol-Transition MR 參數"""

    # BB 參數（沿用 EWT-008 Att1）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（10日高點回檔上限）
    pullback_lookback: int = 10
    pullback_cap: float = -0.08

    # 品質過濾（沿用 EWT-008 Att1）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10

    # Capitulation strength filter
    # mode: "2dd_floor" | "1d_floor"
    capitulation_mode: str = "2dd_floor"
    capitulation_threshold: float = -0.015

    cooldown_days: int = 10


def create_default_config() -> EWT009Config:
    return EWT009Config(
        name="ewt_009_vol_transition_mr",
        experiment_id="EWT-009",
        display_name="EWT Post-Capitulation Vol-Transition MR",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 EWT-008）
        stop_loss=-0.040,  # -4.0%（同 EWT-008）
        holding_days=20,
    )
