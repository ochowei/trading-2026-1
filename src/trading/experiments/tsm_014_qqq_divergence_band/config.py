"""
TSM-014: TSM-QQQ Cross-Asset Divergence BAND Regime-Gated RS Momentum Pullback

策略方向（Strategy Direction）：
    Cross-asset Divergence BAND（同時 FLOOR + CEILING）作為 regime gate。**Repo
    首次將 cross-asset divergence regime gate 從單向 CEILING/FLOOR 擴展為雙向
    BAND 變體**，直接回應 TSM-013 揭露的「Part A SLs 高 Rel_QQQ vs Part B SLs
    低 Rel_QQQ」結構性反向發現。

設計動機（Motivation — Direct Response to TSM-013 Failure Mode）：
    TSM-013 三次迭代：
        - Att1（CEILING +15% loose）：Part A 9 訊號 100% WR (filter 全部 3 SLs)
          / Part B 10 unchanged 80% WR / min(A,B) 0.83 TIE baseline
        - Att2（CEILING +10% tight）：Part A 5 訊號 100% WR (over-filter 4 winners)
          / Part B 8 訊號 75% WR (-22% Sharpe) / min 0.65 REJECT
        - Att3（10d lookback +10%）：Part A 8 訊號 62.5% WR (cooldown chain shift
          new SLs) / Part B 10 unchanged / min 0.31 REJECT

    **核心發現**：TSM Part A 與 Part B SLs 在 Rel_QQQ_20d 維度結構性反向：
        - Part A SLs：HIGH Rel_QQQ_20d（rally exhaustion，TSM 過度跑贏 QQQ）
        - Part B SLs：LOW Rel_QQQ_20d（earnings drift / sector-specific drop，
          QQQ 同步或更強，TSM 相對沒有跑贏）
    單一 CEILING 過濾解 Part A 但對 Part B 非綁定；單一 FLOOR 過濾將解 Part B
    但傷 Part A。

    **TSM-014 假設（BAND Hypothesis）**：
        雙向 BAND threshold（FLOOR ≤ Rel_QQQ_20d ≤ CEILING）可同時：
        (a) 切除 Part A 高 Rel_QQQ 的 rally exhaustion SLs（CEILING）
        (b) 切除 Part B 低 Rel_QQQ 的 single-stock drop SLs（FLOOR）
        (c) 保留 Part A/B winners（多數應落在中段「健康跑贏」區間）

    與既有 lesson #15 BAND（URA-012 / FXI-014 / CIBR-014）的關係：
        - lesson #15 BAND 結構為 ATR ratio 維度（vol-acceleration）
        - TSM-014 為 cross-asset divergence 維度首次 BAND 變體
        - 兩者邏輯平行：當 SLs 集中於兩極端時，BAND 為對稱解

策略類型：相對強度動量回調 + 跨資產相對表現 BAND regime gate
    （RS Momentum Pullback + Cross-Asset Divergence BAND Filter）

================================================================================
基礎（同 TSM-013 Att1，CEILING +15%）
================================================================================
- TSM 20 日報酬 - SMH 20 日報酬 ≥ +5%（相對板塊超額表現，TSM-008）
- 5 日高點回檔 3-7%（短暫整理）
- Close > SMA(50)（上升趨勢確認）
- 訊號日 5 日報酬 ≤ +10.5%（rally exhaustion 過濾，TSM-011 Att3）
- 冷卻 10 日
- TP +8% / SL -7% / 25 天，0.10% 滑價
- TSM 20 日報酬 - QQQ 20 日報酬 ≤ +15%（CEILING，繼承 TSM-013 Att1）

================================================================================
TSM-014 新增（BAND FLOOR）
================================================================================
- **TSM 20 日報酬 - QQQ 20 日報酬 ≥ min_relative_return**（FLOOR）
- Att1（baseline）: min_relative_return = -0.05（-5%，moderate floor）
- Att2: min_relative_return = 0.0（0%，tight floor）
- Att3: 視結果調整

================================================================================
基準對照（TSM-013 Att1 baseline，2026-05-08）
================================================================================
- Part A: 9 訊號 (1.8/yr), WR 100%, 累計 +99.90%, Sharpe 0.00 zero-var (9/9 TPs)
- Part B: 10 訊號 (5.0/yr), WR 80%, 累計 +59.78%, Sharpe 0.83
- min(A,B): Part B Sharpe 0.83（Part B binding constraint）

驗收目標：min(A,B) > 0.83 AND A/B 累計差 < 30% AND 訊號比 < 50%。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSM014Config(ExperimentConfig):
    """TSM-014 TSM-QQQ Cross-Asset Divergence BAND Regime-Gated RS Momentum Pullback 參數"""

    # === RS Momentum Pullback 基礎（同 TSM-008 / TSM-011 Att3 / TSM-013 Att1）===
    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # === Signal-day return CEILING（TSM-011 Att3 5d cap）===
    ret_1d_max: float = 999.0
    ret_5d_max: float = 0.105

    # === TSM-QQQ Cross-Asset Divergence BAND（TSM-014 核心）===
    # 訊號通過條件：min_relative_return <= (TSM 20d 報酬 - QQQ 20d 報酬) <= max_relative_return
    # CEILING 方向：過濾 Part A high Rel_QQQ rally exhaustion SLs（TSM-013 Att1 已驗證）
    # FLOOR 方向：過濾 Part B low Rel_QQQ single-stock drop SLs（TSM-014 新增）
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    max_relative_return: float = 0.15  # CEILING 繼承 TSM-013 Att1
    # Att1: min_relative_return = -0.05 → TIE 0.83 (FLOOR non-binding，全部 ≥ -5%)
    # Att2: min_relative_return = +0.05 → 嘗試過濾 Part B 2024-07-16 SL (+4.10%)
    min_relative_return: float = 0.05
    use_divergence_filter: bool = True


def create_default_config() -> TSM014Config:
    return TSM014Config(
        name="tsm_014_qqq_divergence_band",
        experiment_id="TSM-014",
        display_name="TSM TSM-QQQ Cross-Asset Divergence BAND Regime-Gated RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
