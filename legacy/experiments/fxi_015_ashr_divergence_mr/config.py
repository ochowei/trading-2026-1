"""
FXI-015: FXI-ASHR Cross-Asset Divergence Filter on ATR-Band MR

策略方向：在 FXI-014 Att2 框架（pullback + WR + ClosePos + ATR ratio BAND
[1.05, 1.35]）之上，新增「FXI vs ASHR 10 日相對報酬下限」作為 cross-asset
divergence regime gate（lesson #20 v3 family v11 候選擴展）。

核心假設（repo 首次：FXI 為 target、ASHR 為 anchor 的 cross-asset
divergence regime gate）：
- FXI = iShares China Large-Cap ETF（持有 H 股、HK 上市，offshore 流動性）
- ASHR = Direxion CSI 300 ETF（持有 A 股、上海/深圳上市，onshore 流動性）
- FXI vs ASHR 的 N 日相對報酬差 = HK 與大陸資金流分歧度
  - Div_10d ~ 0：兩個市場同步，無結構性分歧
  - Div_10d 大幅負向（FXI 弱於 ASHR）：HK 特定壓力（資本外流、監管打壓、
    地緣政治）導致 H 股結構性弱於 A 股
- 當 Div_10d 過於負向時，FXI 的 capitulation MR 訊號失敗率升高，因為
  H 股弱勢來源不只是「跌深 = 反彈」的 mean-reversion 結構，而是 HK 自身
  的 idiosyncratic 賣壓延續

FXI-014 Att2 baseline 之 Part A 殘餘 3 SLs trade-level Div_10d：
- 2021-11-03 SL: Div_10d = -2.68pp（Evergrande 違約 + 監管打壓持續）
- 2022-03-02 SL: Div_10d = **-8.55pp**（俄烏戰 + 上海封城雙重 HK 拋售，
                  ASHR 0.14% 接近持平 vs FXI -8.69%）
- 2023-02-06 SL: Div_10d = -2.23pp（Spy balloon + post-reopening 失望）

Part A 21 個 baseline 訊號的 Div_10d 分布：
- TPs（18 筆）: Div_10d ∈ [-5.95, +3.05]，最深 -5.95（2022-10-21 TP）
- SLs（3 筆）: Div_10d ∈ [-8.55, -2.23]
- Surgical sweet spot：Div_10d 閾值 ∈ (-8.55, -5.95)，即 floor >= -7% 可
  乾淨切除 2022-03-02 deep SL 而不傷害任何 TPs

Part B 5 個訊號的 Div_10d 分布：
- 4 winners + 1 small expiry 的 Div_10d ∈ [-5.44, +1.37]
- 最深 winner div_10d = -5.44pp（2024-01-22 TP）
- floor >= -7% 對 Part B 完全非綁定（無 winners 受影響）

預期 Att1（floor >= -7%）：Part A 21 → 20 訊號，移除 1 個 -5.10% SL，
                          Part A Sharpe 1.01 → 估計 ~1.10-1.15
                          Part B 完全保留 5 訊號 / Sharpe 1.61 不變

跨資產脈絡（lesson #20 v3 family v11 候選）：
- 既有成功案例：TLT-014 (TLT-SPY 20d FLOOR, rate vs equity)、TSLA-017
  (TSLA-QQQ 20d FLOOR, high-vol AI vs broad tech)、INDA-012 (INDA-EEM 60d
  CEILING, single-country EM vs broad EM)、EWZ-009 (EWZ-EEM 10d CEILING,
  commodity-EM vs broad EM)、NVDA-021 (NVDA-QQQ 20d CEILING, AI mega-cap
  vs broad tech)、GLD-016 (GLD-DXY 5d direction)
- 既有失敗案例：COPX-014 (commodity miners 雙 Part SLs 反向)、USO-026
  (commodity ETF 雙 Part 結構性反向)、TSM-013 (multi-driver 個股雙向)、
  EEM-EFA、EEM-FXI
- 本實驗為 repo 首次「H-share ETF 為 target + A-share ETF 為 anchor」
  variant，捕捉 HK-mainland 結構性分歧

迭代結果：
- Att1（rel_lookback=10, min_rel_return=-0.07，surgical 2022-03-02 filter）：
  待運行
- Att2: 待 Att1 結果決定方向（tighten 或 loosen）
- Att3: robustness check

成交模型：同 FXI-014（next_open_market 進場、limit_order Day TP、
stop_market GTC SL、next_open_market 到期、滑價 0.1%、悲觀認定）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI015Config(ExperimentConfig):
    """FXI-015 FXI-ASHR Cross-Asset Divergence Filter on ATR-Band MR 參數"""

    # === Pullback / WR / ClosePos / ATR BAND（同 FXI-014 Att2）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05
    pullback_cap: float = -0.12

    wr_period: int = 10
    wr_threshold: float = -80.0

    close_position_threshold: float = 0.4

    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.05
    atr_ratio_ceiling: float = 1.35

    # === FXI-ASHR Cross-Asset Divergence Filter (FXI-015 核心新增) ===
    # ASHR = Direxion Daily CSI 300 ETF（A-share onshore anchor）
    anchor_ticker: str = "ASHR"
    # lookback：Att1 10d（surgical 但被 cooldown chain shift 中性化）；
    # Att2 20d（更廣 regime 視窗，可同時過濾 2022-03-02 + 2022-03-09 chain shift）；
    # Att3 robustness check.
    rel_lookback: int = 20
    # min_rel_return：FXI N 日報酬 - ASHR N 日報酬 >= 此閾值。負向越深越嚴。
    # Att1 10d/-0.07（TIE baseline 1.01，cooldown chain shift 中性化：2022-03-02
    #              SL 過濾後 2022-03-09 chain shift fires SL -5.09%）。
    # Att2 ★ 20d/-0.08（PARTIAL SUCCESS min(A,B) **1.21** +19.8% vs baseline 1.01；
    #              同時過濾 2022-03-02 主 SL + 2022-03-09 chain shift SL，
    #              代價為 2 TPs（2019-03-08, 2021-12-17, Div_20d ≤ -11.5pp）；
    #              Part A 21→18 訊號, WR 85.7%→88.9%, Sharpe 1.01→1.21；Part B
    #              5 訊號完全不變 1.61）。
    # Att3 20d/-0.07（更嚴 threshold ablation，min(A,B) 1.16 -4% vs Att2 — 過嚴
    #              移除 2022-10-21 TP，確認 -0.08 為結構性甜蜜點）。
    min_rel_return: float = -0.08

    cooldown_days: int = 10


def create_default_config() -> FXI015Config:
    return FXI015Config(
        name="fxi_015_ashr_divergence_mr",
        experiment_id="FXI-015",
        display_name="FXI-ASHR Cross-Asset Divergence MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,
        stop_loss=-0.050,
        holding_days=20,
    )
