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
- DIA-012（1.0% vol）：1d cap + 3d cap 雙維度方向成功
- SPY-009（1.0% vol）：1d floor 方向成功
- EWJ-005 Att2（1.15% vol）：1d floor <= -0.5% → min(A,B) 0.60→0.70（+16.7%）

EWT 1.41% vol 落在 lesson #19 已驗證 vol 區間內。半導體驅動單一國家 EM ETF 結構接近
EWJ（DM 已開發但同樣亞洲 export-led），先測試 VGK-008 Att2 / EWJ-005 Att1 已驗證的
2DD floor <= -2.0%。

Att1（2DD floor <= -2.0%，VGK-008 Att2 / EEM-014 / INDA-010 / EWJ-005 Att1 直接移植）：
- Part A 7/85.7%/Sharpe 0.91 cum +17.89%
- Part B 3/100%/std=0 cum +10.87%
- min(A,B)† 0.91（+59.6% vs EWT-008 baseline 0.57）
- **失敗分析**：-2.0% 過嚴：2019-05-09（2d -1.69%）+ 2023-03-15（2d -1.87%）winners
  兩筆被同時過濾，且因 2019-05-09 移除引入 2019-05-13 cooldown shift 新 SL
  （lesson #19）。Sharpe 大幅改善但 Part A 訊號從 9 縮至 7，A/B 訊號比惡化至
  7:3 = 2.33:1。需測試更精準閾值或改用 1d 維度。
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
    capitulation_threshold: float = -0.02

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
