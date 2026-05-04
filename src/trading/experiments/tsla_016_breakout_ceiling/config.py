"""
TSLA-016: Signal-Day Direction Filter on Multi-Week Regime BB Squeeze Breakout
TSLA Multi-Period Direction-Filter Regime Breakout Configuration

策略方向：直接驗證 FCX-014 提出的明確跨資產假設——將 lesson #19 family 的
「signal-day return CEILING」維度跨資產移植至 TSLA-015 Att3 的 BB Squeeze
Breakout 框架（高波動 AI 個股，3.72% 日波動）。

================================================================================
跨資產假設來源（FCX-014 配置直接記錄）：
    "BB Squeeze Breakout + signal-day ceiling 可能適用於其他高 vol mining/
     commodity 類型（COPX-011 銅礦 ETF、NVDA-012、TSLA-015 等既有 BB Squeeze
     框架），閾值依 SLs 3d 分布調整。"
================================================================================

Repo 第 4 個 lesson #19 family 框架類型驗證軌跡：
- MR 框架 ✓（DIA-012、SPY-009、EWT-009、IWM-013、GLD-014、INDA-011、SIVR-018、
  URA-013、VGK-008、IBIT-009、EEM-014 等 11+ 次 floor / cap 成功）
- RS Momentum 框架 ✓（TSM-011 Att3 5d ceiling +10.5% rally exhaustion，
  min(A,B) 0.79→0.83 +5%）
- BB Squeeze Breakout（商品/礦業單股，FCX）✓（FCX-014 Att1 3d ceiling +12.0%，
  min(A,B) 0.55→0.64 +16%）
- BB Squeeze Breakout（高波動 AI 個股，TSLA）— 本實驗首次驗證 → **REJECTED**

================================================================================
基準：TSLA-015 Att3（已執行驗證 2026-04-26，當前全域最優 min(A,B) 0.53）
================================================================================
- Part A: 11 訊號 / WR 72.7% / Sharpe 0.84 / cum +82.29%（8 TP / 2 SL / 1 EX）
- Part B: 6 訊號 / WR 66.7% / Sharpe 0.53 / cum +26.25%（4 TP / 2 SL）
- min(A,B) **0.53**，A/B 年化 cum 12.78%/yr vs 12.36%/yr（gap 3.3% < 30% ✓）
- A/B 訊號比 1.36:1（gap 26.7% < 50% ✓）

trade-level Part A 訊號日期（11）：
  2019-07-10 TP / 2019-10-14 TP / 2019-12-16 TP / 2020-06-01 TP / 2020-06-30 TP
  / 2020-08-17 TP / 2020-11-18 TP / 2021-07-30 SL / 2021-09-24 TP / 2023-03-31 SL
  / 2023-12-14 EX -1.38%
trade-level Part B 訊號日期（6）：
  2024-06-17 TP / 2024-09-23 SL / 2024-12-06 TP / 2025-05-12 TP / 2025-09-11 TP
  / 2025-11-03 SL

目標：Sharpe > 0.53，維持 A/B 平衡（cum gap < 30%、訊號比 < 50%）。

================================================================================
參數設計依據（vol-scaled cross-asset port）
================================================================================
TSLA 日波動 ~3.72% / FCX 日波動 ~3.0%，scaling factor 約 1.24x。
- FCX-014 Att1：3d ceiling 12.0% 為 robust sweet spot 區間 [11.0%, 12.0%]
- 跨資產移植初值：12.0% × 1.24 ≈ 15.0%（Att1）
- 5d 軸：TSM-011 Att3 5d ceiling +10.5%（TSM 日波動 ~2.0%），TSLA 移植：
  10.5% × (3.72/2.0) ≈ 19.5%（Att3 5d 軸切換，採 22% 較寬 threshold）

================================================================================
迭代結果
================================================================================
Att1（3d ceiling 15.0%）— FAILED：
  Part A 10/70.0%/Sharpe **0.76** cum +65.72%（過濾 2020-08-17 TP）/
  Part B 5/60.0%/Sharpe **0.37** cum +14.77%（過濾 2025-05-12 TP）/
  min(A,B) **0.37**（vs baseline 0.53，**-30%**）
  失敗根因：3d ceiling 15% 過濾 2 winners（2020-08-17 COVID rapid recovery、
  2025-05-12 post-tariff rebound），完全未過濾任何 Part A/B SLs。
  TSLA winners 包含極端 3d 報酬（>15%），losers 集中於 moderate 3d 報酬（<15%），
  ceiling filter 結構性反向選擇。

Att2（3d ceiling 20.0%）— NON-BINDING：
  Part A 11/72.7%/Sharpe **0.84** cum +82.29%（與 baseline 完全相同）/
  Part B 6/66.7%/Sharpe **0.53** cum +26.25%（與 baseline 完全相同）/
  min(A,B) **0.53**（與 baseline 持平，無改善）
  確認 [15%, 20%] 區間僅含 2 winners 無 SLs，3d ceiling 結構性失敗。

Att3（5d ceiling 22.0%，軸切換）— FAILED：
  Part A 10/70.0%/Sharpe **0.76** cum +65.72%（過濾 2020-08-17 TP，5d 報酬亦 >22%）/
  Part B 6/66.7%/Sharpe **0.53** cum +26.25%（保留 2025-05-12 TP，5d <22%）/
  min(A,B) **0.53**（與 baseline 持平）
  Part A Sharpe 退化 0.84 → 0.76（**-10%**），Part B 完全不變（5d 22% 對 Part B 非綁定）。
  軸切換確認：5d ceiling 同樣對 TSLA 結構性反向選擇——濾除 2020-08-17 winner
  （COVID recovery 的 5d 累計報酬亦極端高），未捕捉任何 SL；2021-07-30 SL 與
  2023-03-31 SL 的 5d 報酬皆 < 22% 不被過濾。

================================================================================
核心結論（lesson #19 family v13 邊界擴展）
================================================================================
1. **Repo 首次拒絕 lesson #19 ceiling 維度於高波動 AI 個股 BB Squeeze 框架**：
   FCX-014（3% 商品/礦業單股）成功 → TSLA-016（3.72% AI 個股）失敗。
   失敗邊界精煉：BB Squeeze Breakout + signal-day return ceiling 的有效資產
   結構為「商品/礦業驅動因子主導 + winners 與 losers 在 signal-day return
   分布上有方向性區分」；不適用於「事件驅動 + AI bull regime + winners
   跨越整個 return spectrum」資產類型。

2. **TSLA winners/losers 的 signal-day return 分布為反向結構**：
   - Winners（12 筆）：2020-08-17 / 2025-05-12 兩筆 3d 與 5d 累計報酬皆於極端
     高位（>15% / >22%）；其餘 winners 落於 moderate 區間
   - Losers（4 筆）：所有 SLs 的 3d 報酬皆 < 15%、5d 報酬皆 < 22%，集中於
     moderate 區間，與多數 winners 重疊
   - 結果：return ceiling filter 系統性過濾 winners 而非 losers

3. **跨資產 ceiling 維度有效性的結構性先決條件**：
   參考 FCX-014 Part A 4 SLs 中 1 SL（2021-04-15）3d 12.61% 與所有 winners 的
   max 3d 11.50% 形成 1.11pp 緩衝帶——FCX 上有「至少一個 SL 的 signal-day
   return 高於所有 winners 的 max return」結構，使 ceiling filter 可單向過濾。
   TSLA 上不存在此結構：所有 SLs 落在 winners 的中間 return band 內，無單向
   分隔線。**未來 cross-asset port 需先做 trade-level signal-day return 分布
   分析**，確認「至少一筆 loser 的 N 日報酬 > 多數 winners 的 N 日報酬」結構
   存在後再嘗試 ceiling filter。

4. **TSLA-015 Att3 維持全域最優**（16 次實驗、49+ 次嘗試）。**lesson #22
   buffered SMA regime gate 仍為 TSLA BB Squeeze Breakout 唯一有效的多期
   regime filter**；TSLA 結構性 Sharpe 0.53 上限仍待跨維度（^VXN forward-looking
   implied vol、TSLA-QQQ cross-asset divergence、^VIX BANDS 等）突破。

5. **未來方向**：
   - 已驗證失敗：lesson #19 ceiling（TSLA-013 T-1 cap、TSLA-016 3d/5d ceiling）
   - 待嘗試：^VXN forward-looking implied vol regime gate（lesson #24 family，
     repo 首次 ^VXN 應用）、TSLA-QQQ cross-asset divergence（lesson 25/26 family）、
     ^VIX BANDS U-shape regime gate（XBI-017 family 首次擴展至高 vol 個股）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA016Config(ExperimentConfig):
    """TSLA-016 Multi-Period Direction-Filter Regime Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 TSLA-015）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime 過濾（lesson #22，同 TSLA-015 Att3 sweet spot）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.99  # buffered 1% per TSLA-015 Att2/Att3

    # === 多週期波動 regime 過濾（TSLA-015 Att3 已驗證冗餘，停用）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = False

    # === 訊號日方向過濾（lesson #19 family，本實驗新增）===
    # 3 日累計報酬上限：要求 signal_day_3d_return <= max_signal_day_3d_return
    # Att1: 0.15（vol-scaled FCX-014 Att1 12% × 1.24x）— FAILED min(A,B) 0.37
    #       過濾 2 winners（2020-08-17 Part A、2025-05-12 Part B）但保留所有 SLs
    #       3d ceiling 對 TSLA 結構性反向選擇（winners 3d ≥ losers 3d）
    # Att2: 0.20（threshold 寬鬆檢測）— 與 baseline 完全相同（17 個訊號全部 3d <= 20%）
    #       確認 [15%, 20%] 區間僅含 winners 無 SLs，3d ceiling 結構性失敗
    # Att3: stop using 3d ceiling, switch to 5d ceiling axis
    # 預設 None 為 Att3 配置（停用 3d，啟用 5d）
    # 設為 None 表示停用此過濾
    max_signal_day_3d_return: float | None = None

    # 5 日累計報酬上限：要求 signal_day_5d_return <= max_signal_day_5d_return
    # Att3: 0.22（vol-scaled TSM-011 Att3 +10.5% × (TSLA 3.72% / TSM 2.0%) ≈ 19.5%
    #       round up to 22% for safer initial threshold；軸切換測試 5d 是否有
    #       不同選擇性，因 5d 為更廣 momentum window 可能捕捉真正 rally exhaustion）
    #       — FAILED：濾除 2020-08-17 winner（5d 亦 > 22%），未捕捉任何 SL，
    #       Part A 退化 -10%，Part B 完全不變，min(A,B) 持平 baseline 0.53
    # 設為 None 表示停用此過濾
    max_signal_day_5d_return: float | None = 0.22

    # 1 日報酬上限：要求 signal_day_1d_return <= max_signal_day_1d_return
    # 設為 None 表示停用此過濾（FCX-014 已驗證 1d ceiling 在 3d 啟用時冗餘）
    max_signal_day_1d_return: float | None = None


def create_default_config() -> TSLA016Config:
    """建立預設配置（Att3：5d ceiling 22%，最終配置／cross-asset 失敗紀錄）"""
    return TSLA016Config(
        name="tsla_016_breakout_ceiling",
        experiment_id="TSLA-016",
        display_name="TSLA Multi-Period Direction-Filter Regime Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
