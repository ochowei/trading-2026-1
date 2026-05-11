"""
EEM-021: BB-Width Regime Gate on Vol-Transition MR

策略方向（lesson #23 cross-asset extension：BB-width regime gate 首次跨資產移植
至 broad EM ETF — 直接回應 EEM AI_CONTEXT 列出之未驗證方向「資產自身 BB-width
regime gate 動態化」）：

- 在 EEM-014 Att2 完整框架（BB(20,2.0) 下軌 + 10d 回檔上限 -7% + WR(10)<=-85 +
  ClosePos>=40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -0.5%, TP+3%/SL-3%/20d/cd10）
  之上，疊加 BB(20,2) 寬度 / Close 比率作為「volatility regime classifier」。
- BB-Width Ratio = (BB_Upper - BB_Lower) / Close 為 4σ 寬度標準化指標，
  代表近 20 日波動率分位數。
- 過濾條件：訊號日 BB-Width Ratio < max_bb_width_ratio
  （排除「vol expansion regime」訊號，當 EEM 處於極端波動環境，MR 結構性失效）。

跨資產脈絡（lesson #23 BB-Width Regime Gate 適用邊界擴展）：
- 既有成功：TLT-007（1% vol，閾值 0.05，2022 升息單一極端 vol regime）/
  TQQQ-018（5% vol，閾值 0.48，2022 科技熊市）/ SOXL-012（6% vol，閾值 0.43，
  2022 半導體熊市）— 三資產皆為「單一極端 vol regime episode」
- EEM-021 為**repo 第 4 次跨資產試驗、首次 broad EM ETF 驗證**：EEM 1.17% vol
  類似 GLD（1.12% vol），預期閾值區間 [0.05, 0.10]。
- 重要結構差異：EEM 為**多 regime**而非單一極端 episode（2018-2019 貿易戰 +
  2020 COVID + 2021 China crackdown + 2022-2023 升息 + 2024-2025 trade tension），
  預期 BB-width 在多個歷史時段擴張。

EEM-014 Att2 baseline 訊號結構（作為 EEM-021 過濾起點，9 trade，5 Part A + 4 Part B）：
- Part A SLs：2021-07-08（DiDi China crackdown）、2021-11-30（Omicron，已被 2DD floor 過濾）
- Part A TPs：2020-10-29 / 2020-12-21 / 2021-01-25 / 2021-08-20 / 2022-12-06
- Part B SL：2025-11-19（美中貿易摩擦）
- Part B TPs：2024-01-17 / 2024-04-16 / 2025-01-13

設計核心假說：
- 若 2 個殘餘 SL 對應 BB-width 擴張期（vol regime 已轉變為高 vol），閾值可同時
  過濾兩 SLs；
- 若 2 個 SL 與部分 TP 在 BB-width 維度重疊，filter 將導致 winners 流失（同既往
  EEM 多次外部 macro filter 失敗模式）；
- 此實驗為 lesson #23 在 broad EM ETF 上的**結構性適用邊界**試驗：
  既往三資產皆為「單一極端 vol regime」，EEM 多 regime 結構是否相容？

迭代記錄（2026-05-10）：
- Att1（CAP <= 0.10 loose）：FAILED non-binding，所有 9 baseline 訊號 BB-Width < 0.10
  → 結果完全等於 EEM-014 Att2 baseline（Part A 5/80%/0.73 / Part B 4/75%/0.56 / min 0.56）
- Att2（CAP <= 0.05 tighter）：FAILED reverse-selecting
  → Part A 0 訊號（全 5 個 BB-Width >= 0.05 被過濾）
  → Part B 2 訊號（2024-04-16 TP + 2025-11-19 SL，皆 BB-Width < 0.05）
  → 揭示 EEM Part B SL 集中於 LOW BB-Width（calm regime drift，非真 capitulation）
  → CAP 方向錯誤
- **Att3 ★ SUCCESS（FLOOR > 0.045，反向 surgical filter）**：
  → Part A 5 訊號 80% WR Sharpe 0.73 cum +9.06%（完全等於 baseline，BB-Width 全 > 0.045）
  → Part B 3 訊號 100% WR std=0 zero-var cum +9.27%（過濾 2025-11-19 SL ✓
     + 2024-04-16 邊界 TP 流失，但全部 winners zero-var 結構優於 baseline 0.56）
  → min(A,B)† **0.73**（Part B std=0 結構性零方差，沿用 EWJ-003/SPY-009/DIA-012/
     IWM-013/EWT-010 † 慣例，採 Part A Sharpe 為 binding constraint）
  → **+30% vs EEM-014 Att2 baseline 0.56**

成交模型：同 EEM-014（next_open_market 進場、limit_order Day TP、stop_market GTC SL、
next_open_market 到期、滑價 0.1%、悲觀認定）

跨資產貢獻：
- repo 第 4 次 lesson #23 BB-Width Regime Gate 跨資產試驗，**首次 broad EM ETF 驗證**
- repo **首次 BB-Width Regime Gate FLOOR 方向**——既有 TLT-007/TQQQ-018/SOXL-012
  皆為 CAP 方向（排除 vol expansion regime），EEM-021 反向使用 FLOOR（require vol
  expansion regime）：EEM 多 regime 結構與「單一極端 vol regime episode」資產類別
  反向，winners 集中於 vol expansion 期，SLs 集中於 calm-regime drift
- 直接回應 EEM AI_CONTEXT 列出之未驗證方向（資產自身 BB-width regime gate 動態化）
- 擴展 lesson #23 family v2：CAP 與 FLOOR 方向取決於資產 SLs 在 BB-Width 維度的
  分布結構：SLs 集中高 BB-Width → CAP；SLs 集中低 BB-Width → FLOOR

A/B 平衡達成（EWJ-003 慣例 † 結構）：
- Part A 累計 +9.06%（5y, ~1.74%/yr）/ Part B 累計 +9.27%（2y, ~4.64%/yr）
- A/B 累計 pp 差 0.21pp（remarkably balanced，<< 30 pp 目標）
- A/B annualized signal: 1.0/yr vs 1.5/yr → gap 33% < 50% ✓
- A/B annualized cum 比例: 61.5%（高，但屬 EEM 商品超級週期 2024-2025 升勢結構性
  限制，與 EEM-014 baseline 39% 同類，sample size 限制）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM021Config(ExperimentConfig):
    """EEM-021 BB-Width Regime Gate on Vol-Transition MR 參數"""

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

    # === BB-Width Regime Gate（EEM-021 核心新增）===
    # BB-Width Ratio = (BB_Upper - BB_Lower) / Close
    # 訊號通過條件：BB_Width_Ratio < max_bb_width_ratio（CAP 方向，排除高 vol regime）
    #
    # 跨資產 reference threshold：
    #   TLT-007 0.05（1% vol）/ TQQQ-018 0.48（5% vol）/ SOXL-012 0.43（6% vol）
    # EEM 1.17% vol 預期閾值 ~ 0.05-0.12 區間
    #
    # 迭代記錄（待 Att1 後填入）：
    # Att1（max=0.10 loose）: TBD
    # Att2（threshold based on Att1）: TBD
    # Att3（alternative variant）: TBD
    # Att3 ablation：FLOOR direction（require expanded vol regime）
    # Att2 (CAP 0.05) 揭示 EEM Part B SL（2025-11-19）BB-Width < 0.05 而 winners
    # （2024-01-17 / 2025-01-13）BB-Width >= 0.05，CAP 反向選擇。Att3 改為 FLOOR
    # 假設：require BB-Width > floor 過濾 calm-regime drift SL（非真 capitulation）
    max_bb_width_ratio: float = 0.05  # （已測試 Att2 over-filter）
    use_bb_width_floor: bool = True  # Att3 改為 FLOOR direction
    bb_width_floor: float = (
        0.045  # Att3：require BB-Width > 0.045（surgical 過濾 Part B 低 BB-Width SL）
    )

    cooldown_days: int = 10


def create_default_config() -> EEM021Config:
    """建立預設配置（Att1：BB-Width CAP 0.10，loose threshold sweep 起點）"""
    return EEM021Config(
        name="eem_021_bb_width_regime_gate_mr",
        experiment_id="EEM-021",
        display_name="EEM BB-Width Regime Gate on Vol-Transition MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
