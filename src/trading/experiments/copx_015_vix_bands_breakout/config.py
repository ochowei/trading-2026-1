"""
COPX-015: ^VIX Implied-Vol Regime Filter on Multi-Week Regime-Aware BB Squeeze
         Breakout

策略方向（Strategy Direction）：
    在 COPX-011 Att3（regime BOX [k_min=1.00, k_max=1.09] BB Squeeze Breakout，
    min(A,B) 0.64，當前全域最優，A/B 年化 cum gap 66.4% > 30% 目標 ❌）基礎上
    疊加 **^VIX forward-looking implied-vol regime gate**。

    **Repo 第 3 次 lesson #24 family BANDS/FLOOR 變體驗證 + 首次 ^VIX FLOOR
    變體於商品/礦業 ETF**：lesson #24 family 至 2026-05-07 為止已成功變體：
      - LEVEL CAP（TLT-013 ^MOVE <= 130）
      - DIRECTION（XLU-013 ^MOVE 3d / USO-025 ^OVX 3d / GLD-015 ^GVZ 10d）
      - BANDS exclude mid（XBI-017 ^VIX (17, 22)，Pullback MR 框架）
      - FLOOR（FCX-015 ^VIX > 14，BB Squeeze Breakout 框架，repo 首次 FLOOR）
    COPX-015 跨資產 / 跨類別測試：將 FCX-015 ^VIX FLOOR 從「商品/礦業單股突破」
    移植至「商品/礦業 ETF 突破」框架。

動機（Motivation）：
    COPX-011 Att3 現存 A/B annualized cum gap 66.4%（>30% 目標）原因：
      Part A（2019-2023, 5.0yr）: 10 訊號 / WR 80% / cum +40.03% / Sharpe 0.72
                                   年化 ~8.0%/yr，含 1 SL（2019-04-01）+ 3 EX
      Part B（2024-2025, 2.0yr）:  2 訊號 / WR 50% / cum  +5.35% / Sharpe 0.64
                                   年化 ~2.65%/yr，1 TP + 1 EX -1.54%
    Part A 受惠於 2020-2021 COVID 復甦 + 商品超級週期；Part B 為 2024-2025
    銅價震盪期，TPs 集中於 Part A 明顯。

    Trade-level 觀察 COPX-011 Att3 殘餘 Part A 1 個 SL（2019-04-01 VIX 13.40）
    + 2 個負 EX（2023-07-12 VIX 13.54 / 2023-12-13 VIX 12.19 — 後者報酬
    +3.42% 但被排除於後續分析）以及 Part B 1 個 EX -1.54%（2025-06-26
    VIX 16.59）。FCX-015 Att2 成功將 FCX BB Squeeze A/B cum gap 從 52.5% 降至
    7.1%，cross-asset hypothesis on 礦業/商品 ETF 為 COPX-015 主要驗證重點。

    **核心假說（U-shape regime hypothesis 鏡像）擴展至 commodity/mining ETF
    突破策略**：
        FCX-015 發現 FCX BB Squeeze 殘餘 SLs **集中於 low-VIX calm regime**
        （與 XBI MR 結構相反）。COPX 為同類資產（commodity/mining）但為 ETF
        分散結構，假說 SLs 同樣集中於 low-VIX calm regime：BB Squeeze 突破
        在低 VIX 時為 false breakout（市場 calm 但 COPX 自身突破缺乏 broad-
        market vol 證實）。VIX FLOOR > 14 應系統性過濾這類 calm-period false
        breakouts。

    與 lesson #5 「趨勢濾波器+MR=災難」的區分：
        COPX-015 使用「broader market regime classifier」（implied vol level
        floor），非 COPX 自身趨勢過濾。COPX-011 SMA(20)/SMA(60) regime BOX 為
        own-asset trend regime gate（lesson #22），COPX-015 ^VIX FLOOR 為
        cross-asset regime gate（lesson #24 FLOOR），兩者結構性正交。

策略類型：BB Squeeze Breakout + 多週期趨勢 regime BOX + ^VIX FLOOR
    （Breakout + Own-Asset Trend Regime Box + Implied Vol Floor Gate）

================================================================================
基礎（同 COPX-011 Att3 ★ 2026-04-28，BB Squeeze 全域最優）
================================================================================
- BB(20, 2.0) 60d 30th pct squeeze + 5d 內擠壓 + 收盤 > Upper BB
- Close > SMA(50)
- regime BOX：1.00 <= SMA(20) / SMA(60) <= 1.09（lesson #22 + COPX 新發現）
- 冷卻 12 日
- TP +7% / SL -6% / 20 天，0.15% 滑價

================================================================================
基準對照（COPX-011 Att3 ★ 2026-04-28，BB Squeeze 全域最優）
================================================================================
- Part A: 10 訊號, WR 80.0%, 累計 +40.03%, Sharpe 0.72, MDD -6.57%
- Part B:  2 訊號, WR 50.0%, 累計  +5.35%, Sharpe 0.64
- min(A,B) **0.64**（+42% vs COPX-007 baseline 0.45）
- A/B 年化 cum 8.0%/yr vs 2.65%/yr（gap 66.4% > 30% ❌ 結構性）
- A/B 訊號比 2.0:1.0 = 2:1（gap 50% boundary）

驗收目標：min(A,B) > 0.64（COPX 全域最優突破），且 A/B cum gap < 30%
（任務 acceptance criterion），訊號比 gap < 50%。
================================================================================

================================================================================
Att1（mode=floor, vix_low=14.0）：FCX-015 Att2 sweet spot 直接移植
================================================================================
參數：vix_filter_mode="floor", vix_low_threshold=14.0
結果：
  Part A: 7 訊號 WR **100.0%** Sharpe **2.81** cum +51.26% MDD -5.74%
    （+290% Sharpe vs baseline 0.72；+11.23pp cum vs baseline 40.03%）
    過濾 3 訊號（VIX <= 14 calm regime，全為 SL/EX）：
      - 2019-04-01 SL VIX 13.40（baseline 唯一 SL）
      - 2023-07-12 EX -4.63% VIX 13.54
      - 2023-12-13 EX +3.42% VIX 12.19（正 EX，副作用過濾）
  Part B: 2 訊號（**完全等於 baseline**）, WR 50.0%, Sharpe 0.64, cum +5.35%
    - 2025-06-05 TP +7.00% VIX 18.48（>14 通過 FLOOR）
    - 2025-06-26 EX -1.54% VIX 16.59（>14 通過 FLOOR）— 未被 FLOOR 過濾
  min(A,B) **0.64**（與 baseline TIE，Part B 為 binding constraint）
分析：
  - **Part A 大幅改善（+290% Sharpe）驗證 FCX-015 cross-asset hypothesis**：
    FLOOR 14 cleanly 過濾全部 Part A SL/EX 失敗，WR 100% / PF 9999+
  - **Part B 結構性無法改善**：兩筆 Part B 訊號 VIX 皆 > 14，FLOOR 不綁定
    Part B 含 2025-06-26 EX -1.54%（VIX 16.59，rally exhaustion 1d=6.07% spike），
    其特徵與 Part B TP（VIX 18.48，1d=1.71%）在 VIX 維度 (16.59 vs 18.48)
    過於接近，純 VIX FLOOR 無法切分
  - **A/B 失衡惡化**：cum gap 73.9%（vs baseline 66.4%）；signal gap 71.4%
    （vs baseline 50%）—— Part A 大幅改善 = A/B 進一步發散，違反 acceptance
  - **整體驗收**：min(A,B) 不嚴格優於 baseline，但 Part A 提供 290% Sharpe
    改善 + 100% WR，跨資產假設正向驗證

================================================================================
Att2（mode=floor, vix_low=17.0）：targeted Part B EX filter
================================================================================
參數：vix_filter_mode="floor", vix_low_threshold=17.0
結果：
  Part A: 5 訊號 WR **100%** Sharpe **2.32** cum +32.12%（仍優於 baseline 0.72）
    額外過濾 2 訊號（vs Att1）：2021-04-15 TP（VIX 16.57）、2019-12-10 TP（VIX 15.68）
  Part B: 1 訊號（zero-variance）TP +7%（**過濾 2025-06-26 EX VIX 16.59 ≤ 17**）
  min(A,B)† Part A binding **2.32**（Part B std=0 用 † 慣例同 EWJ-003/SPY-009）
  A/B annualized cum 6.42%/yr vs 3.5%/yr → gap 45.5%（>30% ❌）
  A/B 訊號比 5:1 → gap 80%（>50% ❌）
分析：
  - 成功過濾 Part B EX -1.54%，但 Part B 僅 1 訊號（0.5/yr）統計顯著性不足
  - 雖 † 慣例可宣稱 min 2.32 但訊號比 80% gap 嚴重違反 50% 目標
  - **REJECT**：sample size 失衡，無法接受 1-trade Part B 為穩健結論

================================================================================
Att3（mode=floor, vix_low=13.0）：threshold sensitivity (loosen)
================================================================================
參數：vix_filter_mode="floor", vix_low_threshold=13.0
結果：
  Part A: 9 訊號 WR 77.8% Sharpe **0.69** cum +35.40% MDD -6.57%
    （**接近 baseline 0.72**，僅過濾 12.19 EX +3.42%；保留 13.40 SL + 13.54 EX -4.63%）
  Part B: 2 訊號 完全不變 0.64
  min(A,B) **0.64**
分析：
  - 放寬至 FLOOR 13 將 13.40 SL 與 13.54 EX -4.63% 放回，Part A 退化至接近 baseline
  - **確認 FLOOR 14 為 sweet spot**：往下 1pt（Att3 13）即放行關鍵 SL/EX
  - Part B 兩筆訊號 VIX 皆 > 13，無變化（與 Att1 結論一致）

================================================================================
Final 結論（Att1 為最終配置，但 min(A,B) 與 baseline 結構性 TIE）
================================================================================
- Att1（FLOOR 14）為最佳——Part A Sharpe 0.72→2.81（+290%）+ WR 80%→100%
- Att1 min(A,B) 0.64 與 baseline TIE（Part B 結構性無法被 VIX 過濾改善）
- A/B 失衡未達標（cum gap 73.9%、signal gap 71.4%）
- Att2 證實 Part B EX 可過濾但 sample size 退化至 1，REJECT
- Att3 確認 FLOOR 14 為 sweet spot
- **跨資產發現**：FCX-015 FLOOR 14 假說在 COPX BB Squeeze Breakout 同樣有效
  於 Part A 失敗訊號過濾（FLOOR 方向正確），但 COPX Part B sample size 結構性
  限制（regime BOX 後僅 2 訊號）使 min(A,B) 無法經由單一 VIX FLOOR 改善
- **新跨資產規則（lesson #24 family v6 + lesson #19 family 邊界擴展）**：
  ^VIX FLOOR 變體於 commodity/mining BB Squeeze Breakout 框架在
  「Part A SL/EX 集中於 calm regime + Part B 訊號數 >= 3」雙條件下有效
  （FCX 個股滿足，COPX ETF 因 Part B 僅 2 訊號失敗第二條件）—— sample size
  precondition 為跨資產 FLOOR 移植的新規則
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX015Config(ExperimentConfig):
    """COPX-015 ^VIX FLOOR Filter on BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 COPX-011）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 12

    # === 多週期趨勢 regime BOX（lesson #22 + COPX-011 BOX 發現，同 COPX-011 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00
    sma_regime_ratio_max: float = 1.09

    # === ^VIX regime gate（COPX-015 核心新增，lesson #24 family）===
    # 模式 (vix_filter_mode):
    #   "floor":             通過條件 VIX > vix_low_threshold（要求 VIX 高於 floor）
    #   "cap":               通過條件 VIX <= vix_high_threshold
    #   "bands_exclude_mid": 通過條件 VIX <= low OR VIX > high（XBI-017 模式）
    #   "bands_keep_mid":    通過條件 vix_low < VIX <= vix_high
    #   "off":               不啟用 VIX 過濾
    #
    # 最終配置：Att1 FLOOR 14.0
    #   Part A 10→7 訊號 WR 80%→100% Sharpe 0.72→2.81 cum 40.03→51.26%
    #   Part B 不變（兩訊號 VIX > 14 不綁定）
    #   min(A,B) 0.64（與 baseline TIE，Part B 為 binding constraint）
    vix_ticker: str = "^VIX"
    vix_filter_mode: str = "floor"
    vix_low_threshold: float = 14.0
    vix_high_threshold: float = 22.0


def create_default_config() -> COPX015Config:
    """建立預設配置（Att1 ★ 最佳配置：vix_floor=14.0）"""
    return COPX015Config(
        name="copx_015_vix_bands_breakout",
        experiment_id="COPX-015",
        display_name="COPX VIX FLOOR Filter on BB Squeeze Breakout",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.07,
        stop_loss=-0.06,
        holding_days=20,
    )
