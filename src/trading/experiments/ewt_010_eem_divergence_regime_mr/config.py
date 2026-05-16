"""
EWT-010: EWT–EEM Cross-Asset Divergence Regime-Gated MR

延伸 EWT-009 Att3 全域最優框架（BB(20,2.0) 下軌 + 10日回檔上限 -8% + WR(10)≤-80
+ ClosePos≥40% + ATR(5)/ATR(20)>1.10 + 2DD floor ≤ -1.5%，TP+3.5%/SL-4.0%/20d/
cd10），新增「EWT–EEM 跨資產 divergence regime gate」作為品質過濾器，目標過濾
EWT-009 Att3 Part A 唯一殘餘 binding SL（2019-05-09 中美貿易戰關稅升級，-4.10%）。

跨資產脈絡（cross-asset divergence regime gate family，3-for-1）：
- SUCCESS：TSLA-017（TSLA−QQQ +81%，個股 vs 自身指數）/ TLT-014（TLT−SPY +393%，
  純利率 vs 股票）/ GLD-016（GLD−USD，純貨幣 vs 美元）
- FAIL：SIVR-019（SIVR−USD，白銀 ~50% 工業需求 → 與美元 DECOUPLED；family v4
  首次失敗，確立「結構性對手必須 DRIVER-PURE 單因子反向」前置條件）
- 空遠端 artifact `ewt_010_ewt_eem_2d_divergence_mr` 獨立指向「EWT vs EEM 2d
  divergence」方向；本實驗以**獨立 module 名稱**避免 branch-divergence artifact
  衝突，並以 EEM（EWT 的母體 EM 指數，可交易 ETF）為 divergence 軸。

Trade-level 預分析（EWT-009 Att3 binding 為 Part A 唯一殘餘 SL 2019-05-09，
EEM 對齊 EWT signal day，2d 累計報酬 divergence = EWT_2d − EEM_2d，單位 %）：

| Signal     | Grp    | EWT_2d | EEM_2d | DIV(EWT−EEM) |
|------------|--------|--------|--------|--------------|
| 2019-05-09 | A SL   | -1.69  | -1.72  | **+0.03**    |  中美貿易戰
| 2019-08-02 | A TP   | -3.29  | -2.92  | -0.37        |
| 2020-01-27 | A TP   | -3.71  | -4.23  | +0.52        |
| 2020-09-24 | A TP   | -3.42  | -2.01  | -1.41        |
| 2021-07-27 | A TP   | -2.15  | -3.88  | +1.73        |
| 2021-08-17 | A TP   | -3.49  | -2.73  | -0.76        |
| 2022-01-28 | A TP   | -1.77  | -0.67  | -1.10        |
| 2023-03-15 | A TP   | -1.87  | -1.66  | -0.21        |
| 2023-07-06 | A TP   | -3.34  | -2.62  | -0.72        |
| 2024-04-16 | B TP   | -3.70  | -1.95  | -1.75        |
| 2025-01-13 | B TP   | -4.23  | -2.37  | -1.86        |
| 2025-11-18 | B TP   | -3.84  | -1.67  | -2.16        |

**預分析判定（NOT separable，預測 documented-failure，family v4 第 2 次失敗）**：
- binding SL 2019-05-09 DIV = **+0.03**（EWT_2d -1.69 ≈ EEM_2d -1.72）—— 中美
  貿易戰關稅衝擊為**廣域 China/EM co-move**，台灣未對 EM 產生 idiosyncratic
  divergence，與 winners DIV ∈ [-2.16, +1.73] 完全交錯（NVDA-017/EEM-016 反例9/
  TSM-012 同族 idiosyncratic SL）。
- INVERTED for OOS：3 筆 Part B winners DIV 全為最負（-1.75/-1.86/-2.16，台灣
  顯著弱於 EM）→ divergence FLOOR 將屠殺全部 OOS 訊號且完全不觸及 SL。
- EWT **非 DRIVER-PURE**：EWT 本身為 EEM 成分（ρ≈0.85，正相關），其「divergence」
  在 binding-loss 日 ≈ 0（貿易戰同步衝擊全 EM）→ 違反 family v4 前置條件
  （SIVR-019 規則：結構性對手須單因子反向）。

迭代計畫（三次迭代，predict→confirm）：
  Att1：EWT−EEM 2d divergence CEILING ≤ 0.0%（GLD-016 Att1 絕對 divergence
        ceiling 精確類比，filter「台灣未隨 EM 同步 capitulation」之假強勢）
        → 預測：移除 SL（+0.03>0）但非外科式同殺 2 筆 Part A winners
        （2020-01-27 +0.52、2021-07-27 +1.73）→ degenerate notch REJECT
  Att2：EWT−EEM 2d divergence FLOOR ≥ -1.0%（TLT-014/GLD-016 Att2 相對
        divergence floor 精確類比，「僅在台灣未顯著弱於 EM 時進場」）
        → 預測：不移除 SL（+0.03≥-1.0）且屠殺全部 3 筆 Part B winners
        （-1.75/-1.86/-2.16<-1.0）→ inverted catastrophic REJECT
  Att3：EWT−EEM **1d** divergence CEILING ≤ 0.0% lookback ablation
        → 預測：1d-DIV SL = -0.20 ≤ 0.0 連 SL 都不過濾，confirm 無可分
        cross-asset divergence lookback（family v4 第 2 次失敗確認）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT010Config(ExperimentConfig):
    """EWT-010 EWT–EEM Cross-Asset Divergence Regime-Gated MR 參數"""

    # ===== EWT-009 Att3 全域最優 base（沿用，不調整）=====
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

    # ===== EWT-010 核心新增：EWT–EEM 跨資產 divergence regime gate =====
    use_divergence_gate: bool = True
    divergence_ticker: str = "EEM"
    divergence_lookback: int = 2
    # mode: "ceiling" → EWT_Nd − EEM_Nd <= divergence_threshold
    #       "floor"   → EWT_Nd − EEM_Nd >= divergence_threshold
    divergence_mode: str = "ceiling"
    divergence_threshold: float = 0.0  # Att1 預設：CEILING ≤ 0.0%


def create_default_config() -> EWT010Config:
    return EWT010Config(
        name="ewt_010_eem_divergence_regime_mr",
        experiment_id="EWT-010",
        display_name="EWT EWT–EEM Divergence Regime-Gated MR",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（EWT TP 沿用 EWT-009）
        stop_loss=-0.040,  # -4.0%（沿用 EWT-009）
        holding_days=20,
    )
