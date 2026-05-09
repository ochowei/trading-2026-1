"""
TSM-018: ATR(5)/ATR(20) BAND Volatility-Acceleration Filter on RS Momentum
TSM ATR Ratio BAND Filter on RS Momentum Pullback Configuration

策略方向（lesson #15 family v3 cross-strategy 移植，repo 首次 ATR ratio BAND
變體於 RS Momentum 框架）：
在 TSM-011 Att3（含 5d return CEILING）之上加入 ATR(5)/ATR(20) BAND 過濾，
嘗試藉由限制訊號日波動率加速度區間捕捉「健康回檔反彈」訊號。

跨資產靈感來源：
- CIBR-014 Att2：ATR(5)/ATR(20) ∈ (1.15, 1.40] BAND 於 BB lower hybrid MR 框架
  成功（min 提升 +37%）
- FXI-014 Att2：ATR(5)/ATR(20) BAND 於 ATR-band MR 框架成功
- URA-013 Att2：multi-period capitulation strength filter 於 MR 框架成功

三次迭代結果（全部 REJECT vs baseline TSM-011 Att3 min 0.83）：

- Att1（atr_ratio ∈ (1.15, 1.40]，CIBR-014 直接移植）：
  Part A 6 訊號 / WR 50% / Sharpe -0.03 / cum -2.35%
  Part B 5 訊號 / WR 80% / Sharpe 0.83 / cum +26.40%
  min(A,B) -0.03 REJECT — BAND 過嚴切除 6 個 Part A 訊號（原 12 → 6），
  cooldown chain shift（lesson #19）引入 3 個新 SLs（2021-01-22 / 2022-01-13 /
  2023-01-24 三筆 ATR ratio 均處於 (1.15, 1.40] 中段）。

- Att2（atr_ratio ∈ (1.00, 1.20]，放寬至 RS Momentum 訊號日典型加速度區間）：
  Part A 4 訊號 / WR 75% / Sharpe 0.65 / cum +17.04%
  Part B 5 訊號 / WR 60% / Sharpe 0.27 / cum +8.74%
  min(A,B) 0.27 REJECT — Part B 退化 -67% Sharpe，cooldown chain shift 將原
  baseline Part B 兩個 SLs（2024-07-16 / 2024-10-30）替換為 (2024-07-08 /
  2024-11-01) 兩個新 SLs，淨效果為 SLs 數量未減反增（baseline 2 → Att2 2，
  但 winners 5 → 3）。

- Att3（atr_ratio_floor 非綁定 0.50, ceiling 1.10，CEILING-only 過濾 in-crash）：
  Part A 6 訊號 / WR 66.7% / Sharpe 0.65 / cum +24.63%
  Part B 6 訊號 / WR 83.3% / Sharpe 0.98 / cum +36.52%
  min(A,B) 0.65 REJECT — Part B Sharpe 改善至 0.98（+18% vs baseline），但
  Part A 退化至 0.65（-24%）使 min 為 0.65；A/B 累計差 32.6% > 30% target ❌。
  CEILING 1.10 過濾 1 個 Part A SL（2024-07-16 ATR 1.18 結構由 chain shift 釋放
  進 Part A 不存在 — 此 SL 為 Part B 訊號），主要過濾 Part A 大量 winners。

核心失敗發現（lesson #15 family v3 cross-strategy 邊界擴展）：
1. **Repo 首次 ATR ratio BAND 於 RS Momentum 框架失敗**——既有成功案例
   CIBR-014 / FXI-014 / URA-013 皆為 MR 框架（capitulation 訊號日 ATR
   結構性高）；TSM RS Momentum Pullback 訊號日為「上升趨勢中淺回檔」，
   ATR ratio 集中於 1.0-1.15 較窄帶，BAND 無區分力。
2. **Part A/B SLs 在 ATR ratio 維度反向**：Part A SLs（2021-01 / 2022-01 /
   2023-01 為 macro shock 拉回）ATR ratio 高（>1.15）；Part B SLs
   （2024-07-16 / 2024-10-30 earnings/macro pullback）ATR ratio 1.10-1.20
   中段。單一 BAND 結構性無法雙 Part 同步改善——同 TSM-013/014（QQQ
   divergence）/ TSM-015（AAPL divergence）/ TSM-016（BB-Width）/
   TSM-017（earnings exclusion）失敗模式平行。
3. **lesson #19 cooldown chain shift 在 RS Momentum + ATR BAND 組合下
   結構性放大反向選擇**——Att2 過濾 baseline 兩個 Part B SLs 但 chain
   shift 引入兩個新 SLs，淨效果零改善。
4. **TSM Part B 0.83 binding constraint 第 6 次結構性無解確認**：
   TSM-013（QQQ CEILING）/ TSM-014（QQQ BAND）/ TSM-015（AAPL anchor）/
   TSM-016（BB-Width）/ TSM-017（earnings exclusion）/ TSM-018（ATR BAND）
   六次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產，未來方向應為：
   (a) SOXX 半導體指數 anchor（注意 TSM 為成分股自我參考），
   (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting)，
   (c) 完全替代 framework（lesson #22 multi-week regime + RS Momentum 組合
       但避免 lesson #21 失敗結構），
   (d) Volume-normalized z-score（vs absolute ratio threshold）解決 A/B
       regime asymmetry。

設計目標（未達成）：
- min(A,B) Sharpe 突破 TSM-011 Att3 的 0.83 — 未達成（最佳 Att3 0.65）
- A/B 累計差距 < 30% — Att3 32.6% 略超
- A/B 訊號比 < 50% gap — Att3 1:1 達成
- 通過成交模型（execution model）回測 — ✓
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMAtrBandRSConfig(ExperimentConfig):
    """TSM ATR(5)/ATR(20) BAND on RS Momentum 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # Signal-day return CEILING（沿用 TSM-011 Att3）
    ret_5d_max: float = 0.105

    # ATR(5)/ATR(20) BAND（TSM-018 新增）
    atr_fast_period: int = 5
    atr_slow_period: int = 20
    # Att3: CEILING-only 過嚴 in-crash acceleration，floor 設極低值非綁定
    atr_ratio_floor: float = 0.50  # 非綁定 floor
    atr_ratio_ceiling: float = 1.10  # 過濾 in-crash 加速訊號


def create_default_config() -> TSMAtrBandRSConfig:
    return TSMAtrBandRSConfig(
        name="tsm_018_atr_band_rs",
        experiment_id="TSM-018",
        display_name="TSM ATR(5)/ATR(20) BAND on RS Momentum",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
