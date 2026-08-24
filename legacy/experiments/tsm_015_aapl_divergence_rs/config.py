"""
TSM-015: TSM-AAPL Cross-Asset Divergence Regime-Gated RS Momentum Pullback

策略方向（Strategy Direction）：
    Cross-asset divergence regime gate 使用「主要客戶 AAPL」為 anchor，**repo 首次
    AAPL anchor 試驗於任何資產**。直接回應 TSM-013 / TSM-014 揭露的 Part B SLs
    在 TSM-QQQ 維度結構性無區分力的核心限制。

設計動機（Motivation — Direct Response to TSM-013/014 Failure Mode）：
    TSM-013（CEILING）三次迭代與 TSM-014（BAND）三次迭代結論：
        - TSM-QQQ_20d 維度 Part B SLs（2024-07-08 / 2024-10-30）落在 winners 分布
          中段 [+1.48%, +12.37%]，**單一 QQQ-based threshold 結構性無區分力**
        - TSM-013 Att1 已將 Part A 推至結構性最優（zero-var all TPs cum +99.90%）
        - TSM-014 文件明確建議：「未來需嘗試 (a) 不同 anchor (如 SOXX 半導體指數
          / AAPL 主要客戶 / NVDA 已驗證 pair 失敗), (b) 不同 lookback (5d/60d),
          (c) 完全替代 framework」

    **TSM-015 假設（AAPL 主要客戶 anchor 假說）**：
        AAPL 為 TSM 最大客戶（~25% 營收，iPhone/Mac SoC 製造），二者具經濟結構
        共同因子（半導體景氣、消費電子需求週期），但 AAPL 為單一客戶單股而非
        broad benchmark。TSM-AAPL 20d divergence 預期較 TSM-QQQ：
        (1) 過濾「客戶轉單 / TSM 操作問題」訊號（TSM 大幅落後 AAPL → 公司特定
            因素，AAPL 製造商進度未受影響）—— 對應 Part B 2024-07-08 / 2024-10-30
            SLs 假說：當時 TSM 因 Trump comments / 地緣政治急跌但 AAPL 相對穩定
        (2) 維持 Part A rally exhaustion 過濾力（TSM 過度跑贏 AAPL 同樣訊號 rally
            exhaustion）—— 但需 trade-level 驗證

策略類型：相對強度動量回調 + 主要客戶 cross-asset divergence regime gate
    （RS Momentum Pullback + Major-Customer Cross-Asset Divergence Filter）

================================================================================
基礎（同 TSM-013 Att1 完整框架，含 CEILING 過濾 Part A rally exhaustion）
================================================================================
- TSM 20 日報酬 - SMH 20 日報酬 ≥ +5%（相對板塊超額表現，TSM-008）
- 5 日高點回檔 3-7%（短暫整理）
- Close > SMA(50)（上升趨勢確認）
- 訊號日 5 日報酬 ≤ +10.5%（rally exhaustion 過濾，TSM-011 Att3）
- 冷卻 10 日
- TP +8% / SL -7% / 25 天，0.10% 滑價

================================================================================
TSM-015 新增（AAPL FLOOR）
================================================================================
- **TSM 20 日報酬 - AAPL 20 日報酬 ≥ min_relative_return_aapl**（FLOOR）
  - Att1 baseline: min_relative_return_aapl = -0.05（-5% lenient floor，trade-level
    觀察 baseline 訊號分布）
  - Att2: 視 Att1 結果決定（surgical filter 命中 Part B SLs）
  - Att3: 視 Att1/Att2 結果決定（可能擴展為 TSM-AAPL FLOOR + TSM-QQQ CEILING
    多 anchor 組合，repo 首次「single asset 多 anchor stack」）

================================================================================
基準對照（TSM-011 Att3 baseline，2026-05-02）
================================================================================
- Part A: 12 訊號 (2.4/yr), WR 83.3%, 累計 +74.10%, Sharpe 0.86
- Part B: 10 訊號 (5.0/yr), WR 80%, 累計 +59.78%, Sharpe 0.83
- min(A,B): Part B Sharpe 0.83（Part B binding constraint）

驗收目標：min(A,B) > 0.83 AND A/B 累計差 < 30% AND 訊號比 < 50%。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSM015Config(ExperimentConfig):
    """TSM-015 TSM-AAPL Cross-Asset Divergence Regime-Gated RS Momentum Pullback 參數"""

    # === RS Momentum Pullback 基礎（同 TSM-008 / TSM-011 Att3）===
    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # === Signal-day return CEILING（TSM-011 Att3 5d cap）===
    ret_5d_max: float = 0.105

    # === TSM-AAPL Cross-Asset Divergence BAND（TSM-015 核心）===
    # 訊號通過條件：min_relative_return_aapl <= (TSM 20d - AAPL 20d) <= max_relative_return_aapl
    # FLOOR 方向：過濾客戶轉單 / TSM 公司特定問題訊號（Part B 2024-07-08 假說）
    # CEILING 方向：過濾 TSM 過度跑贏客戶 → 客戶 demand 飽和訊號
    #   （Part B 2024-10-30 假說，TSM 經 Q3 earnings rally 後 vs AAPL 持平 → +7% Rel_AAPL）
    customer_ticker: str = "AAPL"
    aapl_divergence_lookback: int = 20
    # Att1: FLOOR=-5% only → REJECT min 0.50（cooldown chain shift 引入 2 SLs）
    # Att2: BAND [-7%, +5%] → REJECT min 0.42（CEILING +5% 過嚴 over-filter Part A 12→3）
    # Att3: AAPL FLOOR -7% only + TSM-QQQ CEILING +15%（dual-anchor stack）
    min_relative_return_aapl: float = -0.07
    max_relative_return_aapl: float = 0.99
    use_aapl_floor: bool = True
    use_aapl_ceiling: bool = False

    # === TSM-QQQ Cross-Asset Divergence CEILING（TSM-013 Att1 繼承）===
    # Att3: 啟用 + AAPL FLOOR 為 dual-anchor stack（**repo 首次同一 target 雙 anchor stack**）
    benchmark_ticker: str = "QQQ"
    qqq_divergence_lookback: int = 20
    max_relative_return_qqq: float = 0.15
    use_qqq_ceiling: bool = True


def create_default_config() -> TSM015Config:
    return TSM015Config(
        name="tsm_015_aapl_divergence_rs",
        experiment_id="TSM-015",
        display_name="TSM TSM-AAPL Cross-Asset Divergence Regime-Gated RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
