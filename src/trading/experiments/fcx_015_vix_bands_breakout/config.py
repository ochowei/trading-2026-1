"""
FCX-015: VIX Implied-Vol Regime Bands Filter on Multi-Period Direction-Filter
         Regime BB Squeeze Breakout

策略方向（Strategy Direction）：
    在 FCX-014 Att1（Multi-Period Direction-Filter Regime BB Squeeze Breakout，
    min(A,B) 0.64，當前 BB Squeeze 全域最優，A/B cum gap 52.5% > 30% 目標 ❌）
    基礎上，疊加 **^VIX forward-looking implied-vol BANDS regime gate**。

    **Repo 第 2 次 lesson #24 family BANDS 變體 + 首次 BANDS 變體於 BB Squeeze
    Breakout 框架**——既往 lesson #24 跨資產驗證皆為 LEVEL CAP（TLT-013 ^MOVE）
    或 DIRECTION（XLU-013 ^MOVE 3d、USO-025 ^OVX 3d、GLD-015 ^GVZ 10d）。XBI-017
    首次驗證 BANDS 變體於 Pullback MR 框架（min(A,B) 0.46→0.64，+39%）。
    FCX-015 跨策略移植 BANDS 變體至 BB Squeeze Breakout 框架。

動機（Motivation）：
    FCX-014 Att1 現存 A/B cum gap 52.5%（>30%目標）原因：
      Part A（2018-2023, 5.4yr）: 16 訊號 / WR 75% / cum +89.38% / Sharpe 0.69
      Part B（2024-2025, 2.0yr）: 4 訊號 / WR 75% / cum +16.98% / Sharpe 0.64
    Part A 受惠於 2020-2021 COVID 復甦 + 商品超級週期，每年 cum 16.5%/yr；
    Part B 為 2024-2025 銅價震盪期，每年 cum 8.49%/yr。

    Trade-level 觀察 FCX-014 Att1 殘餘 3 Part A SLs（除 2021-04-15 已被 ceiling
    過濾）：
      2019-07-24 SL: 1d 2.49 / 3d 3.92 / 5d 7.96  (low conviction)
      2020-01-13 SL: 1d 4.88 / 3d 2.66 / 5d 5.29  (modest extension)
      2021-11-11 SL: 1d 9.01 / 3d 3.73 / 5d 10.54 (single-day spike)
    這 3 個殘餘 SLs 的 signal-day VIX 假說性分布需驗證；XBI-017 sweet spot
    [17, 22] 為 BANDS 變體第一個 cross-asset 直接移植測試。

    **核心假說（U-shape regime hypothesis）擴展至 commodity/mining 突破策略**：
        FCX BB Squeeze 突破在 broad market 兩個極端 VIX regime 才結構性有效：
            (a) 低 VIX（市場 calm，但 FCX 因銅價/礦業特定觸發突破
                → 板塊內快速延續，Breakout 成功）
            (b) 高 VIX（broad panic 後 V-bounce → 商品週期性反彈帶動 FCX 突破，
                Breakout 成功）
        中等 VIX 帶（vix_low < VIX <= vix_high）為「complacency creep」regime：
        broad market 表面健康但內部 risk-on/off 切換頻繁，false breakout
        增加 → BB Squeeze 突破失敗率上升。

    與 lesson #5 「趨勢濾波器+MR=災難」的區分：
        FCX-015 使用「broader market regime classifier」（implied vol band），
        非 FCX 自身趨勢過濾。FCX-014 SMA(20)>=1.00*SMA(60) 為 own-asset trend
        regime gate（lesson #22），FCX-015 VIX BANDS 為 cross-asset regime gate
        （lesson #24 BANDS），兩者結構性正交。

策略類型：BB Squeeze Breakout + 多週期趨勢 regime gate + signal-day ceiling
    + ^VIX BANDS（Breakout + Regime Filter + Implied Vol Bands Gate）

================================================================================
基礎（同 FCX-014 Att1 ★ 2026-05-02，當前 BB Squeeze 全域最優）
================================================================================
- BB(20, 2.0) 60d 30th pct squeeze + 5d 內擠壓 + 收盤 > Upper BB
- Close > SMA(50)
- SMA(20) >= 1.00 * SMA(60)（lesson #22 multi-week trend regime gate）
- Signal-day 3d 累計報酬 <= +12%（lesson #19 ceiling，rally exhaustion）
- 冷卻 10 日
- TP +8% / SL -7% / 20 天，0.15% 滑價

================================================================================
FCX-015 新增（lesson #24 family BANDS 變體；repo 第 2 次 BANDS）
================================================================================
- **^VIX BANDS regime gate**：排除中等 VIX 帶
- 訊號通過條件：VIX <= vix_low_threshold OR VIX > vix_high_threshold
- 第一輪迭代候選（XBI-017 sweet spot 直接移植）：(17.0, 22.0)

================================================================================
基準對照（FCX-014 Att1 ★ 2026-05-02，BB Squeeze 全域最優）
================================================================================
- Part A: 16 訊號, WR 75.0%, 累計 +89.38%, Sharpe 0.69, MDD -10.09%
- Part B:  4 訊號, WR 75.0%, 累計 +16.98%, Sharpe 0.64
- min(A,B) **0.64**（+16% vs FCX-013 Att3 0.55）
- A/B 年化 cum 16.55%/yr vs 8.49%/yr（gap 52.5% > 30% ❌ 結構性）
- A/B 訊號比 1.6:1（gap 37.5% < 50% ✓）

驗收目標：min(A,B) > 0.64（FCX 全域最優突破），且 A/B cum gap < 30%
（任務 acceptance criterion），訊號比 gap < 50%。
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX015Config(ExperimentConfig):
    """FCX-015 VIX BANDS Filter on BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 FCX-014）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime（lesson #22，同 FCX-014）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === 訊號日方向過濾（lesson #19 family，同 FCX-014 Att1）===
    max_signal_day_3d_return: float | None = 0.12

    # === ^VIX regime gate（FCX-015 核心新增，lesson #24 family）===
    # 模式 (vix_filter_mode):
    #   "bands_exclude_mid": 通過條件 VIX <= low OR VIX > high（XBI-017 模式）
    #   "floor":             通過條件 VIX > vix_low_threshold（要求 VIX 高於 floor）
    #   "cap":               通過條件 VIX <= vix_high_threshold（要求 VIX 低於 cap）
    #   "bands_keep_mid":    通過條件 vix_low < VIX <= vix_high（保留中等 VIX）
    #   "off":               不啟用 VIX 過濾
    #
    # 迭代紀錄：
    #   Att1（mode=bands_exclude_mid, low=17, high=22）：XBI-017 sweet spot 直接移植
    #     結果：Part A 13/69.2%/0.52/+50.33%, Part B 3/66.7%/0.41/+8.31%, min 0.41
    #     FAIL — 過濾 3 TPs（2021-04-26/2021-12-22/2023-01-06，皆 VIX 17-22 mid 帶）
    #     全 3 SLs 保留（2019-07-24/2020-01-13/2021-11-11→shifted 11-12）
    #     發現：FCX BB Squeeze 突破與 XBI MR 為**反向 VIX U 形**：
    #     FCX TPs 集中於 mid-VIX，SLs 在 low-VIX；XBI 為相反
    #   Att2（依 Att1 trade-level 反向假說調整）
    #   Att3（ablation 或 alternative dimension）
    vix_ticker: str = "^VIX"
    vix_filter_mode: str = "bands_exclude_mid"
    vix_low_threshold: float = 17.0
    vix_high_threshold: float = 22.0


def create_default_config() -> FCX015Config:
    """建立預設配置（Att1：vix_bands (17, 22)）"""
    return FCX015Config(
        name="fcx_015_vix_bands_breakout",
        experiment_id="FCX-015",
        display_name="FCX VIX BANDS Filter on BB Squeeze Breakout",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
