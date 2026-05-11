"""
EEM-020: Multi-Anchor Combined Filter on Vol-Transition MR
(^VIX CAP + EEM-FXI 10d Divergence CEILING)

策略方向（multi-anchor cross-asset divergence ensemble，repo 首次「VIX 維度
CAP × cross-asset divergence CEILING」**異質維度組合**過濾器，直接回應
EEM AI_CONTEXT 列出之未驗證方向「multi-anchor cross-asset divergence ensemble
（multi-dim voting）」）：

- 在 EEM-014 Att2 完整框架（BB(20,2.0) 下軌 + 10d 回檔上限 -7% + WR(10)<=-85 +
  ClosePos>=40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -0.5%, TP+3%/SL-3%/20d/cd10）
  之上，疊加**雙重異質維度過濾**：
    (a) ^VIX 收盤 <= vix_max_level（implied vol LEVEL CAP）
    (b) EEM 10d 報酬 - FXI 10d 報酬 <= max_rel_return（cross-asset divergence CEILING）

- 兩個維度 AND chain 組合，同時過濾**結構性反向**的兩個 Part SLs：
    Part A 殘餘 SL 2021-07-08 DiDi（China-specific shock，FXI 重挫深於 EEM）
      → EEM-FXI 10d divergence > +1%（已 EEM-019 trade-level 驗證）
      → CEILING 維度 binding ✓
    Part B 殘餘 SL 2025-11-19 美中貿易（broad EM macro shock，FXI 同步或更弱）
      → ^VIX 23.66（已 EEM-018 trade-level 驗證）
      → LEVEL CAP 維度 binding ✓

- 設計核心洞察：EEM-019 揭示「Part A/B SLs 在 EEM-FXI divergence 維度結構性反向」
  使單一 threshold 無法雙 Part 同步改善，但**搭配第二維度（VIX）**可分工：
  CEILING 解 Part A China-specific shock；VIX CAP 解 Part B broad EM macro shock。

跨資產脈絡（lesson #20 v3 + lesson #24 family v6 異質維度組合）：
- 既有 multi-dim filter 內**同質方向**組合：
  - USO-028 Att1 ✓（^OVX 5d direction + 3d direction，IV direction 多時框組合）
  - DIA-012 Att2 ✓（1d floor + 3d cap，price-action 雙 horizon）
  - SPY-009 Att2 ✓（同 DIA-012 結構）
  - VOO-005 Att1 ✓（同 SPY-009 結構）
- 本實驗（EEM-020）：**首次「異質維度」（VIX LEVEL CAP × cross-asset divergence CEILING）
  AND chain 組合**——既有同質維度組合多為「同類指標的多時框/多閾值」，本實驗
  探索「不同類指標跨領域組合」是否能解決單一維度 reverse-selection 問題。

EEM 受過濾的兩個 SLs 結構（已從 EEM-018 / EEM-019 trade-level 驗證）：
- 2021-07-08 Part A SL：VIX 19.00（中段，VIX 維度無法過濾）+ RelDiff > +1%（CEILING ✓）
- 2025-11-19 Part B SL：VIX 23.66（高段，VIX <= 23 ✓）+ RelDiff < +1%（CEILING 無法）

預期過濾動態（基於 baseline 9 訊號 5+4 分布）：
- 2021-07-08 Part A SL：VIX 19 通過 CAP 但 RelDiff > +1% 被 CEILING 過濾 ✓
- 2025-11-19 Part B SL：RelDiff < +1% 通過 CEILING 但 VIX 23.66 被 CAP 過濾 ✓
- 雙 SLs 各被一個維度過濾，AND chain 兩個維度互不干擾 winners
- 風險：Part A 高 VIX 25.71 winner（2020 COVID）會被 VIX <= 23 誤殺
- 風險：Part A/B 中 RelDiff > +1% 的 winners（如 2024-01-17、2025-01-13）會被 CEILING 誤殺

迭代設計：threshold sweep 找 sweet spot
- Att1: vix_max=25.0, fxi_max_rel=+0.030（loose，先驗證 filter 方向不過嚴）
- Att2: vix_max=23.0, fxi_max_rel=+0.015（medium，目標雙 SLs 同時過濾）
- Att3: vix_max=22.0, fxi_max_rel=+0.010（tight sweet spot 探尋）

成交模型：同 EEM-014（next_open_market 進場、limit_order Day TP、stop_market GTC SL、
next_open_market 到期、滑價 0.1%、悲觀認定）

關鍵風險：
- EEM-014 baseline 訊號量極小（5 + 4 = 9），雙重過濾極易過嚴 → 統計顯著性損失
- AND chain 兩維度同時過嚴可能歸零訊號（如 0/0）
- Cooldown chain shift（lesson #19）：filter 過濾任何 baseline 訊號可能解除 cooldown
  鎖定釋放新訊號（可能引入新 SL）
- VIX 數據可用性：^VIX 自 1990，FXI 自 2004-10，與 2010+ EEM 數據完整覆蓋

跨資產貢獻（預期，待驗證）：
- repo 首次「異質維度 AND chain 組合 filter」於任何資產
- 直接回應 EEM AI_CONTEXT 列出之未驗證方向（multi-anchor cross-asset divergence ensemble）
- 探索假設：當單一維度 SLs 在該維度上**結構性反向**時，第二**異質維度**可分工解決
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM020Config(ExperimentConfig):
    """EEM-020 Multi-Anchor (^VIX CAP + EEM-FXI CEILING) Combined Filter on Vol-Transition MR 參數"""

    # === BB / 回檔 / WR / ClosePos / ATR（同 EEM-014 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0

    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    wr_period: int = 10
    wr_threshold: float = -85.0
    close_position_threshold: float = 0.40

    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # === 2DD floor（同 EEM-014 Att2 甜蜜點）===
    twoday_return_floor: float = -0.005

    # === ^VIX LEVEL CAP filter（EEM-020 核心新增 - 第一維度）===
    # 目標：過濾 Part B 2025-11-19 SL（VIX 23.66）
    # baseline 訊號 VIX 分布（從 EEM-018 trade-level 文件）：
    #   14.79、17.58、18.40、18.56、19.00 (SL)、19.19、20.56、23.66 (SL)、25.71
    # vix_max = 23 過濾 1 SL (23.66) + 1 TP (25.71)；vix_max = 22 同上
    vix_ticker: str = "^VIX"
    vix_max_level: float = 23.0  # Att1 loose: 25 → Att2 23 → Att3 23 (ablation, isolate VIX)

    # === EEM-FXI 10d divergence CEILING filter（EEM-020 核心新增 - 第二維度）===
    # 目標：過濾 Part A 2021-07-08 DiDi SL（RelDiff > +1.0% per EEM-019 Att2 驗證）
    # FXI = iShares China Large-Cap ETF，EEM 內 ~30% 權重最大單一國家成分
    # Att1 max_rel=+3.0% → Att2 +1.5% → Att3 +1.0%
    fxi_ticker: str = "FXI"
    rel_lookback: int = 10
    max_rel_return: float = 0.10  # Att1 +3% → Att2 +1.5% → Att3 +10% (ablation, CEILING 非綁定)

    cooldown_days: int = 10


def create_default_config() -> EEM020Config:
    """建立預設配置（Att1: vix_max=25.0, fxi_max_rel=+3.0%, loose threshold sweep 起點）"""
    return EEM020Config(
        name="eem_020_multi_anchor_combo_mr",
        experiment_id="EEM-020",
        display_name="EEM Multi-Anchor (^VIX CAP + EEM-FXI CEILING) Combo MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
