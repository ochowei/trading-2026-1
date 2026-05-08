"""
NVDA-020: Volatility-Acceleration Band Filter on Multi-Week Regime-Aware MBPC

策略方向（Strategy Direction）：
    在 NVDA-013 Att3（min(A,B) 0.55 全域最佳）之 multi-week regime-aware MBPC
    框架上，疊加 **ATR(5)/ATR(20) ratio BAND** signal-day vol-acceleration filter，
    為 NVDA-013 AI_CONTEXT 明列「尚未嘗試的方向」中，repo 已驗證跨資產有效之
    入場日波動加速 BAND 過濾器（CIBR-014 / FXI-014 路徑）。

動機（Motivation）：
    NVDA-013 Att3 之 multi-week vol regime 為 ATR(20)/ATR(60) ≤ 1.40（中週期
    波動 regime classifier）。但 entry-day signal-day 之短期波動加速狀態（即
    ATR(5)/ATR(20) ratio）與 entry quality 之關係尚未被任何 NVDA 實驗驗證。

    跨資產證據：
    - CIBR-014 Att2：ATR(5)/ATR(20) BAND ∈ (1.15, 1.40] 將 min(A,B) 0.49→4.08
      （+733%，repo 全域最大幅度突破）
    - FXI-014 Att2：ATR(5)/ATR(20) BAND ∈ (1.05, 1.35] 將 FXI-005 baseline
      推至 min(A,B) 1.27（+135%）
    - 兩者皆為 BB 下軌混合進場 MR 框架（capitulation bounce）

    NVDA-020 假設：multi-week regime-aware MBPC 框架（動量延續類型，與
    capitulation MR 結構性不同）也可能受益於 signal-day ATR ratio BAND 過濾，
    但**最佳邊界可能不同**——MBPC 進場為「Donchian 新高 + 淺回檔 + RSI 中性
    + 多頭 K 棒」，與 capitulation 的「BB 下軌 + 深回檔 + WR ≤ -80」訊號日
    結構迥異。具體假設：
    1. 過低 ATR(5)/ATR(20)（< floor）= 動能不足，淺回檔後缺乏突破延續力，
       可能轉為 chop / fade
    2. 過高 ATR(5)/ATR(20)（> ceiling）= 進場日已 panic spike，多為 late-cycle
       / chop 中的失敗 breakout（Part A 11 SLs 集中區）
    3. 中段 BAND（floor < ratio ≤ ceiling）= 健康延續性 vol regime

策略類型：趨勢跟蹤 / 動量延續 + 多週期 regime gate + 入場日波動加速 BAND
    （Trend-following / Momentum Continuation + Multi-Week Regime Filter +
     Signal-day Vol-Acceleration Band）

================================================================================
基礎（同 NVDA-013 Att3 ★ baseline）
================================================================================
- Donchian 20 日新高，breakout freshness ≤ 10 日
- Close > SMA(50)
- 5 日高點回檔 ∈ [-3%, -8%]
- RSI(14) ∈ [40, 65]
- Close > Open（多頭 K 棒）
- 冷卻 10 日
- TP +8% / SL -7% / 20 天，0.15% 滑價
- Multi-week SMA regime: SMA(20) ≥ 1.00 × SMA(60)（lesson #22）
- Multi-week ATR regime: ATR(20) ≤ 1.40 × ATR(60)（NVDA-013 創新）

================================================================================
NVDA-020 新增（CIBR-014 / FXI-014 跨資產 / 跨策略移植）
================================================================================
- **入場日 ATR ratio BAND**：atr_band_floor < ATR(5)/ATR(20) ≤ atr_band_ceiling
- Att1（NVDA MBPC 適配寬帶）：BAND (0.85, 1.20]
- Att2/Att3：基於 Att1 結果調整

================================================================================
基準對照（NVDA-013 Att3 ★ 全域最佳）
================================================================================
- Part A: 26 訊號, WR 73.1%, 累計 +139.54%, Sharpe **0.55**, MDD -12.06%
- Part B:  7 訊號, WR 85.7%, 累計  +58.62%, Sharpe **2.44**, MDD  -6.31%
- min(A,B): **0.55**

驗收目標：min(A,B) > 0.55，維持 A/B 平衡（cum diff < 30%、訊號比 < 50%）。

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1（BAND ∈ (0.85, 1.20] CIBR-014/FXI-014 直接移植）：FAILED min(A,B) 0.46
    參數：atr_band_floor=0.85, atr_band_ceiling=1.20
    結果：
        Part A: 20 訊號, WR 70.0%, 累計  +78.94%, Sharpe **0.46**
        Part B:  6 訊號, WR 83.3%, 累計  +46.87%, Sharpe **2.22**
        min(A,B): **0.46**（vs NVDA-013 baseline 0.55，-16%）
    失敗分析：
        - BAND 過濾移除 6 訊號（baseline 26→20）：5 winners + 1 loser（WR 83%）
        - **反向選擇**：BAND 移除的 5 winners 多於 1 loser，意味著「中段 ATR 比率
          (0.85, 1.20]」並非 NVDA MBPC 高品質訊號區
        - 不同於 CIBR-014 / FXI-014 capitulation MR 框架（panic + spike clustering）

Att2（CEILING-only ≤ 1.05）：FAILED min(A,B) 0.32
    參數調整：atr_band_floor=0.00, atr_band_ceiling=1.05
    結果：
        Part A: 19 訊號, WR 63.2%, 累計  +47.10%, Sharpe **0.32**
        Part B:  6 訊號, WR 100%,  累計  +54.44%, Sharpe **6.98**（zero-var）
        min(A,B): **0.32**（vs baseline 0.55，**-42%**）
    失敗分析：
        - 移除 7 Part A 訊號（26→19）：**7 winners + 0 losers**（極反向選擇）
        - 由此推斷：**ATR(5)/ATR(20) > 1.05 區間 = 7 wins / 0 losses（100% WR）**
          為 NVDA MBPC 高品質區，與 capitulation MR 預期方向**完全相反**
        - NVDA MBPC 的 entry-day 高 ATR 加速反映 momentum continuation 強度，
          非 panic spike

Att3（FLOOR-only > 1.00 反向 require vol acceleration）：FAILED min(A,B) 0.54
    參數調整：atr_band_floor=1.00, atr_band_ceiling=99.0
    結果：
        Part A: 15 訊號, WR 73.3%, 累計  +64.73%, Sharpe **0.54**
        Part B:  4 訊號, WR 75.0%, 累計  +25.92%, Sharpe **1.72**
        min(A,B): **0.54**（vs baseline 0.55，**-2%** 邊際劣化）
    失敗分析：
        - Floor > 1.00 過濾 11 Part A 訊號（26→15）但 WR 73.3% 與 baseline 73.1%
          幾乎不變，filter 並未選擇性移除 losers
        - Part B 訊號從 7→4 過稀疏（年化 2/yr），Sharpe 從 2.44→1.72 變異性下降
        - **核心結論**：ATR(5)/ATR(20) ratio 維度對 NVDA MBPC 訊號**不具區分力**
          ——losers/winners 在此維度分布重疊，任何閾值（floor/ceiling/BAND）皆
          無法達成 surgical filter

================================================================================
跨資產 / 跨策略貢獻（Cross-Asset / Cross-Strategy Findings）
================================================================================
**NVDA-020 為 ATR(5)/ATR(20) ratio BAND filter 跨策略移植 MBPC 框架的失敗驗證**：

1. **lesson #24 family 邊界擴展**：CIBR-014（min 4.08，+733%）/ FXI-014（min 1.27，+135%）
   兩次 MR + capitulation 框架成功之 ATR(5)/ATR(20) BAND filter，**移植至高 vol mega-cap
   stock + MBPC（momentum continuation）框架完全失敗**——三次迭代（BAND / ceiling /
   floor）均無法超越 NVDA-013 Att3 的 0.55

2. **失敗結構性原因（lesson #20b 失敗家族再擴展）**：
   - capitulation MR 訊號日：價格急跌（BB 下軌 + 深回檔 + WR ≤ -80）—— ATR 高比率
     反映 panic spike，BAND ceiling 區隔「panic 完成 / 仍在加速」
   - MBPC 動量延續訊號日：Donchian 新高後淺回檔 + RSI 中性 + 多頭 K 棒 —— ATR 比率
     不具同向結構（高 ATR 反映 breakout-day momentum，非 panic）
   - **ATR(5)/ATR(20) BAND filter 適用邊界 = 「signal-day vol structure 與 panic
     spike 一致」**——MR / capitulation 框架成立，momentum / breakout-continuation
     框架反向

3. **與 NVDA-013 Att3 vol regime 的差異**：
   - NVDA-013 ATR(20)/ATR(60) ≤ 1.40 為**多週期** vol regime classifier，捕捉
     「過去數週是否處於高波動 transition」（成功）
   - NVDA-020 ATR(5)/ATR(20) 為**入場日**短期波動加速度（失敗）
   - 結論：MBPC 框架的 vol regime 維度有效但只在「中週期」尺度，「日內加速」不具區分力

4. **NVDA 第 12 個失敗策略類型**：擴展失敗清單至 RSI(2) 深 oversold、出場參數、
   動量回調、RS 出場優化、RS 參數探索、MBPC、ADX-RSI(2)、Capitulation Filter MR、
   負 RS Pairs MR、regime-aware RS、cross-asset divergence（partial）、^VXN
   implied vol、Failed Breakdown Reversal、**ATR(5)/ATR(20) BAND filter on MBPC**

NVDA-013 Att3 仍為全域最優（13 次實驗、49+ 次嘗試）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA020Config(ExperimentConfig):
    """NVDA-020 ATR-Acceleration Band Filter on MBPC 參數"""

    # === MBPC 基礎（同 NVDA-013）===
    donchian_period: int = 20
    breakout_recency_days: int = 10
    pullback_lookback: int = 5
    pullback_min: float = -0.03
    pullback_max: float = -0.08
    sma_trend_period: int = 50
    rsi_period: int = 14
    rsi_min: float = 40.0
    rsi_max: float = 65.0
    bullish_close_required: bool = True
    cooldown_days: int = 10

    # === 多週期趨勢 regime（lesson #22，同 NVDA-013 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === 多週期波動 regime（同 NVDA-013 Att3）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = True

    # === 入場日 ATR ratio BAND（NVDA-020 新增；CIBR-014 / FXI-014 路徑）===
    # ATR(atr_band_short) / ATR(atr_band_long) ∈ (atr_band_floor, atr_band_ceiling]
    # Att1 (0.85, 1.20]: FAILED min 0.46（移除 6 訊號中 5 為 winners，BAND 反向選擇）
    # Att2 (0.00, 1.05] (ceiling-only): FAILED min 0.32（ratio ≤ 1.05 area 7 winners
    #     全留下但保留全部 7 losers，ratio > 1.05 area 反為 7 wins/0 losses 高品質）
    # Att3 (1.00, ∞] (floor-only)：require vol acceleration（與 MR 框架方向相反）
    atr_band_short: int = 5
    atr_band_long: int = 20
    atr_band_floor: float = 1.00
    atr_band_ceiling: float = 99.0
    use_atr_band: bool = True


def create_default_config() -> NVDA020Config:
    """建立預設配置（Att1：ATR(5)/ATR(20) BAND (0.85, 1.20]）"""
    return NVDA020Config(
        name="nvda_020_atr_band_mbpc",
        experiment_id="NVDA-020",
        display_name="NVDA Volatility-Acceleration Band Filter on Regime-Aware MBPC",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
