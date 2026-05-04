"""
XBI-017: VIX Implied-Vol Regime Bands Filter Pullback MR

策略方向（Strategy Direction）：
    在 XBI-015 Att2（Multi-Week Regime-Aware Pullback MR，min(A,B) 0.46，
    repo 第 1 次 lesson #22 cross-strategy MR 移植）基礎上，疊加 **^VIX
    forward-looking implied-vol BANDS regime gate**。

    **Repo 第 1 次 lesson #24 family BANDS 變體**——既往 lesson #24 跨資產
    驗證皆為 LEVEL CAP 維度（TLT-013 ^MOVE <= 130）或 DIRECTION 維度
    （XLU-013 ^MOVE 3d、USO-025 ^OVX 3d、GLD-015 ^GVZ 10d）。XBI-017 試
    驗 **BANDS 變體**：排除「中等 VIX 帶（complacency creep zone）」之訊號，
    僅保留低 VIX（隔離型生技下跌、broad market 健康，可恢復）或高 VIX
    （broad capitulation，系統性 V 反彈）之訊號。

動機（Motivation）：
    XBI-015 Att2 殘餘 3 筆 Part A SLs 經實測呈現 **U 型 VIX level 分布**：
        - 2021-05-06 (SL): VIX=18.4, SPY 20d +2.58%, XBI 20d -5.19%
        - 2022-04-19 (SL): VIX=21.4, SPY 20d +0.15%, XBI 20d -4.97%
        - 2023-09-21 (SL): VIX=17.5, SPY 20d -2.28%, XBI 20d -6.54%
    全部 3 筆 SLs 落於 VIX ∈ [17.5, 21.4]「中等 VIX」帶；同時 SPY 20d
    報酬處於 -3% ~ +3% 中性區，既非 broad capitulation（低 VIX 隔離型）
    也非 panic（高 VIX 系統性）。

    對照 XBI-015 Att2 winners 樣本（從各 regime 抽樣）：
        - 2020-05-13 (W): VIX=35.3 → 高 VIX 帶（COVID panic 反彈）
        - 2024-03-14 (W): VIX=14.4 → 低 VIX 帶（市場健康，生技 isolated dip）
        - 2024-11-18 (W): VIX=15.6 → 低 VIX 帶
        - 2024-12-19 (W): VIX=24.1 → 高 VIX 帶
        - 2025-05-07 (W): VIX=23.5 → 高 VIX 帶
        - 2022-05-12 (W): VIX=31.8 → 高 VIX 帶（2022 bear V-bounce）
        - 2019-08-26 (W): VIX=19.3 → 中等 VIX 帶（單一 winner 落在 SL band 內）

    **核心假說（U-shape regime hypothesis）**：
        XBI capitulation MR 在 broad market 的兩個極端 regime 才結構性有效：
            (a) 低 VIX（市場 calm，但 XBI 因 biotech 特定事件 isolated dip
                → 板塊內快速回補，MR 成功）
            (b) 高 VIX（broad panic capitulation → systematic V-bounce 帶動
                XBI 隨 risk asset 反彈，MR 成功）
        中等 VIX 帶（vix_low < VIX <= vix_high）為「complacency creep」regime：
        broad market 表面健康但內部分化（small caps / sector rotation），
        XBI biotech 板塊性 stress 無 broad capitulation 助力 → MR 失效。

    與 XBI-016 Att1 (broad-market macro confirmation gate) 的區分：
        - XBI-016 Att1: QQQ 10d <= -1.5%（要求 broad market 同步弱勢，IWM-015
          pattern port）→ FAILED min(A,B) -0.55，因 XBI SLs 多發於 broad
          market 同步修正期，winners 多發於 biotech-specific 反彈
        - XBI-017: VIX BANDS 排除中段（含 broad 健康 winner 與 broad panic
          winner 兩類），與 XBI-016 方向正交

    與 lesson #5 「趨勢濾波器+MR=災難」的區分：
        XBI-017 使用「broader market regime classifier」（implied vol band），
        非 XBI 自身趨勢過濾——延續 TLT-014 lesson #5 邊界精煉：cross-asset
        regime gate 為合法 MR 過濾維度。

策略類型：均值回歸 + 多週期波動 regime gate + ^VIX BANDS 過濾
    （Mean Reversion + Vol Regime Filter + Implied Vol Bands Gate）

================================================================================
基礎（同 XBI-015 Att2，當前全域最優 ★ 2026-04-30）
================================================================================
- 10 日高點回檔 ∈ [-8%, -20%]
- Williams %R(10) ≤ -80
- ClosePos ≥ 35%
- ATR(20) ≤ 1.10 × ATR(60) vol stability gate
- 冷卻 10 日
- TP +3.5% / SL -5.0% / 15 天，0.1% 滑價

================================================================================
XBI-017 新增（lesson #24 family BANDS 變體；repo 首次）
================================================================================
- **^VIX BANDS regime gate**：排除中等 VIX 帶
- 訊號通過條件：VIX <= vix_low_threshold OR VIX > vix_high_threshold
- vix_low_threshold：候選 16~18
- vix_high_threshold：候選 21~23

================================================================================
基準對照（XBI-015 Att2 ★ 2026-04-30 全域最優）
================================================================================
- Part A: 15 訊號, WR 80.0%, 累計 +25.13%, Sharpe 0.46, MDD -7.09%
- Part B:  6 訊號, WR 83.3%, 累計 +12.71%, Sharpe 0.64
- min(A,B) 0.46
- A/B 年化 cum 4.59%/yr vs 6.16%/yr（gap 25.5%）
- A/B 年化訊號比 1.0:1（gap 0%）

驗收目標：min(A,B) > 0.46（XBI 全域最優突破），維持 A/B 平衡
（年化 cum diff < 30%、訊號比 gap < 50%）。
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI017Config(ExperimentConfig):
    """XBI-017 VIX Implied-Vol Regime Bands Filter Pullback MR 參數"""

    # === 進場指標（同 XBI-015 Att2）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 >= 8%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.35

    # === 多週期波動 regime gate（同 XBI-015 Att2）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.10
    use_vol_regime: bool = True

    # === ^VIX BANDS regime gate（XBI-017 核心新增）===
    # 訊號通過條件：VIX <= vix_low_threshold OR VIX > vix_high_threshold
    # 迭代紀錄（最終 Att1 為最佳）：
    #   Att1 ★（vix_low=17.0, vix_high=22.0）：對齊 3 SLs [17.5, 21.4] 包覆區
    #     Part A 11/90.9%/Sharpe **3.12** cum +41.00% MDD -4.62% / Part B 6/83.3%/0.64/+12.71%
    #     min(A,B) **0.64**（vs XBI-015 Att2 0.46，**+39%**）
    #     A/B 年化 cum 7.10% vs 6.16% gap **13.2% < 30% ✓**；訊號比 2.2:3.0/yr gap 26.7% < 50% ✓
    #     **3 個 XBI-015 Part A 殘餘 SLs 全數過濾**（2021-05-06 / 2022-04-19 / 2023-09-21）
    #   Att2（vix_low=18.0, vix_high=21.0 加嚴）：Part A 13/84.6%/0.62/+27.40% / Part B 0.64
    #     min(A,B) 0.62（-3% vs Att1）。加嚴 1pt 兩端反向放回 1 winner + 1 loser，淨 Sharpe 退步
    #   Att3（vix_low=16.0, vix_high=23.0 放寬）：Part A 9/100%/0.00 zero-var/+36.29%
    #     Part B 5/100%/0.00 zero-var/+18.77%；雙 zero-var 結構，min(A,B) 退化為 0.00
    #     兩端 1pt 過濾掉 2 winners 與 1 loser，純化但統計顯著性下降
    vix_ticker: str = "^VIX"
    vix_low_threshold: float = 17.0
    vix_high_threshold: float = 22.0
    use_vix_bands: bool = True

    cooldown_days: int = 10


def create_default_config() -> XBI017Config:
    """建立預設配置（Att1：vix_bands (17, 22)）"""
    return XBI017Config(
        name="xbi_017_vix_bands_mr",
        experiment_id="XBI-017",
        display_name="XBI VIX Implied-Vol Regime Bands Filter Pullback MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
    )
