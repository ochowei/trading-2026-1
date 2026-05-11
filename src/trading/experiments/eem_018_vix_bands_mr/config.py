"""
EEM-018: ^VIX Implied-Vol Regime BANDS Filter on Vol-Transition MR

策略方向（Strategy Direction）：
    在 EEM-014 Att2（Post-Capitulation Vol-Transition MR：BB(20,2.0) 下軌 +
    回檔上限 -7% + WR(10) <= -85 + ClosePos >= 40% + ATR(5)/ATR(20) > 1.10
    + 2DD floor <= -0.5%，min(A,B) 0.56）框架上，疊加 ^VIX forward-looking
    implied-vol BANDS regime gate（U-shape regime hypothesis 跨資產移植）。

    **Repo 第 2 次 lesson #24 family BANDS 變體**——XBI-017 為首例，本實驗
    為首次跨資產移植至 broad EM ETF。既往 lesson #24 跨資產驗證除 XBI-017
    外皆為 LEVEL CAP 維度（TLT-013 ^MOVE <= 130）或 DIRECTION 維度
    （XLU-013 ^MOVE 3d、USO-025 ^OVX 3d、GLD-015 ^GVZ 10d、EWJ-006
    USDJPY 10d、TLT-014 TLT-SPY 20d）。

動機（Motivation）：
    EEM-014 Att2 baseline 殘餘 Part A SL 結構（trade-level 分析）：
        - 2021-07-08 (SL): DiDi ADR 監管衝擊（中國特定）
        - 2025-11-19 (SL): 美中貿易摩擦升溫（EM-specific）
    Part B 殘餘 SL：
        - 2025-11-19 重複出現（同事件）
    多次 cross-asset divergence filter（EEM-017 EEM-EFA、EEM-016 DXY）皆
    failed — 兩個 SLs 與 EEM 過去 N 日 vs DM peer / DXY 之關係不一致。

    **核心假說（U-shape regime hypothesis 移植）**：
        EEM capitulation MR 在 broad market 兩個極端 regime 才結構性有效：
            (a) 低 VIX（calm regime，EM-specific dip 為 isolated event，
                broad risk-on 環境支撐 EM 反彈）
            (b) 高 VIX（broad panic，systematic V-bounce 帶動 EEM 隨 risk
                asset 反彈，broad capitulation 助力）
        中等 VIX 帶（17 < VIX <= 22）為「complacency creep」regime：
        broad market 表面健康但內部分化（EM 政策衝擊、貿易摩擦延續性壓力），
        EEM 的 capitulation 訊號缺乏 broad rebound 助力 → MR 失效。

    XBI-017 vs EEM-018 結構平行：
        - 兩者皆為 vol-transition MR + 多重技術過濾（pullback / WR / ClosePos）
        - 兩者皆有殘餘 SL 集中於「中性 broad market regime」
        - VIX 中等帶為共通失敗 regime classifier 候選

策略類型：均值回歸 + multi-week vol stability gate + ^VIX BANDS 過濾
    （Mean Reversion + ATR ratio + 2DD floor + Implied Vol Bands Gate）

================================================================================
基礎（同 EEM-014 Att2，當前全域最優 ★ 2026-04-21）
================================================================================
- BB(20, 2.0) 下軌觸及
- 10 日高點回檔 >= -7%（EM 崩盤隔離）
- Williams %R(10) <= -85
- ClosePos >= 40%
- ATR(5) / ATR(20) > 1.10（signal-day panic）
- 2DD floor <= -0.5%（排除淺幅慢漂移）
- 冷卻 10 日
- TP +3.0% / SL -3.0% / 20 天，0.1% 滑價

================================================================================
EEM-018 新增（lesson #24 family BANDS 變體 — repo 第 2 次）
================================================================================
- **^VIX BANDS regime gate**：排除中等 VIX 帶
- 訊號通過條件：VIX <= vix_low_threshold OR VIX > vix_high_threshold
- 候選範圍：vix_low ∈ [16, 18]、vix_high ∈ [21, 23]

================================================================================
基準對照（EEM-014 Att2 ★ 2026-04-21 全域最優）
================================================================================
- Part A: 5 訊號, WR 80.0%, 累計 +9.06%, Sharpe 0.73
- Part B: 4 訊號, WR 75.0%, 累計 +5.89%, Sharpe 0.56
- min(A,B) 0.56
- A/B 累計差 3.17pp，A/B 訊號比 1.25:1

驗收目標：min(A,B) > 0.56（EEM 全域最優突破），維持 A/B 平衡
（年化 cum diff < 30%、訊號比 gap < 50%）。
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM018Config(ExperimentConfig):
    """EEM-018 ^VIX BANDS Regime Gate on Vol-Transition MR 參數"""

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

    # === ^VIX BANDS regime gate（EEM-018 核心新增）===
    # 訊號通過條件：VIX <= vix_low OR VIX > vix_high（排除中等 VIX 帶）
    #
    # 迭代紀錄（threshold sweep all FAILED vs EEM-014 Att2 baseline 0.56）：
    #
    # Att1（vix_low=17.0, vix_high=22.0）：XBI-017 sweet spot 直接移植
    #     → FAILED min(A,B) -0.02
    #     trade-level：Part A 5→1（移除 1 SL 2021-07-08 + 3 TPs，淨 -2 trades）/
    #     Part B 4→2（移除 2 TPs，保留 2025-11-19 SL VIX 23.66 > 22）
    #
    # Att2（vix_low=18.0, vix_high=21.0）：XBI-017 Att2 sweet spot 收緊變體
    #     → FAILED min(A,B) -0.02
    #     trade-level：Part A 5→2（仍移除 SL，但 Part A WR 100% std=0）/
    #     Part B 4→2（同 Att1，2025-11-19 SL VIX 23.66 > 21 仍未過濾）
    #
    # Att3（vix_low=16.0, vix_high=23.0）：寬 BANDS 變體（threshold sweep）
    #     → FAILED min(A,B) -0.02
    #     trade-level：Part A 5→1（更窄保留範圍）/ Part B 4→2（同 Att1，
    #     2025-11-19 SL VIX 23.66 = 23 邊界仍允許通過）
    #
    # Final config kept at Att1（XBI-017 直接移植，最具 cross-asset 比較價值）
    vix_ticker: str = "^VIX"
    vix_low_threshold: float = 17.0
    vix_high_threshold: float = 22.0
    use_vix_bands: bool = True

    cooldown_days: int = 10


def create_default_config() -> EEM018Config:
    """建立預設配置（Att1：vix_bands (17, 22)，XBI-017 sweet spot 直接移植）"""
    return EEM018Config(
        name="eem_018_vix_bands_mr",
        experiment_id="EEM-018",
        display_name="EEM ^VIX BANDS Regime Gate on Vol-Transition MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
