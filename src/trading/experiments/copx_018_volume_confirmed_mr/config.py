"""
COPX Volume-Confirmed Capitulation Mean Reversion (COPX-018)

實驗動機 (Problem statement):
- COPX 全域最優 COPX-011 Att3 BB Squeeze Breakout min(A,B) 0.64, 但 Part B
  僅 2 訊號為 sample size binding constraint, 任何 filter 對 Part B 非綁定
  皆使 min 結構性 TIE.
- COPX-007 vol-adaptive MR baseline (Sharpe 0.45/0.57, min 0.45) 訊號分佈
  較均衡 (Part A 21 訊號 / Part B 10 訊號, signal ratio 1:1.05),
  cum gap 較小, 為更穩健的改進起點.
- 既有 COPX cross-asset macro filter 試驗 (COPX-013/014/015/016/017)
  全部建立於 macro/yield/FX 維度 (rate-curve, GLD, SPY, DXY, ^VIX)
  皆為「外部 macro 情境」過濾, 從未試驗 **資產內生 (asset-intrinsic)
  volume-based** 過濾維度.

嘗試方向 (repo 首次 volume-surge filter 於 COPX 任何框架):
- COPX-007 既有三維度 = pullback (price-level) + WR (oscillator) + ATR ratio
  (volatility range), 全部由 OHLC 衍生; **Volume 為 OHLC 之外的第四維度**.
- 假設 (volume-confirmation hypothesis):
  * 真 panic flush 反彈訊號日 = 大量殺跌 (高參與度) + 收盤跌深 + WR 超賣
    → Volume / SMA(Volume, 20) >= K (高量確認)
  * 慢磨/低量探底 = Volume / SMA(Volume, 20) ~1 或 < 1 (低參與度)
  * COPX-010 已驗證 winners/losers 在 1d/2d return 維度大幅重疊,
    volume 為**獨立第四維度**測試.
- Volume 過濾與既有 ATR(5)/ATR(20) 過濾正交 (價格波幅 vs 成交量參與度)
  雖統計上常相關, 但反映不同訊息 (range expansion vs 廣度買賣壓力).

正交性 (orthogonality):
- COPX-007 ATR ratio: True Range expansion (vol surge of price range)
- COPX-018 Volume ratio: 成交量 surge (broader market participation)
- 兩維度通常正相關但結構不同 (ETF 上 ATR ratio 飆升不必然伴隨 Volume 飆升,
  特別在低成交量市場結構性靜態下).

迭代計畫 (3 iterations max):
- Att1: vol_ratio_threshold = 1.30 (modest 30% above 20-day SMA)
- Att2: 視 Att1 結果調整閾值 (放寬至 1.20 / 收緊至 1.50)
- Att3: 探索替代 volume 維度 (Volume Z-score 60d / down-day volume
  concentration / 5d cumulative volume ratio)

成功判準 (acceptance criteria):
1. min(A,B) Sharpe > 0.64 (COPX 跨框架全域最優, COPX-011 Att3 BB Squeeze)
2. A/B 累計差距 < 30% (COPX-011 baseline 已失敗, MR 框架較具改善空間)
3. A/B 訊號數差距 < 50%
4. 使用 execution model (繼承 ExecutionModelStrategy)
5. 失敗時記錄: 失敗原因 + cooldown chain shift 結構 + 對 lesson #6
   (確認指標的邊際效益遞減) 邊界貢獻
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX018Config(ExperimentConfig):
    """COPX-018 Volume-Confirmed Capitulation MR 參數

    迭代紀錄將在執行後填入.
    """

    # 進場條件 (沿用 COPX-007 Att3 vol-adaptive MR 完整框架)
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    wr_period: int = 10
    wr_threshold: float = -80.0

    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # COPX-018 核心新增: volume filter
    # 模式 (mode):
    #   "ratio_sma_floor": Volume / SMA(Volume, N) >= threshold (high-vol gate)
    #   "ratio_sma_ceil":  Volume / SMA(Volume, N) <= threshold (low-vol gate)
    #   "zscore_60_floor": (Volume - SMA60) / Std60 >= threshold (high-vol gate)
    #   "cum_5d_floor":    SUM(Volume, 5) / SUM(SMA(Volume, 20), 5) >= threshold
    #   "cum_5d_ceil":     SUM(Volume, 5) / SUM(SMA(Volume, 20), 5) <= threshold
    #
    # 迭代紀錄 (3 iterations, Att3 ★ SUCCESS vs COPX-011 跨框架最優 0.64):
    # Att1 (ratio_sma_floor 1.30, high-vol gate): Part A 19/73.7%/0.38
    #   cum +27.64% / Part B 6/66.7%/0.21 cum +4.35% / min 0.21 REJECT.
    #   Volume FLOOR 1.30 系統性移除 4 個 Part B winners
    #   (10→6, Sharpe 0.57→0.21), 反向選擇結構 — COPX 2024-2025 區間
    #   panic flush 訊號日 volume 未 surge (慢量探底反為有效訊號).
    # Att2 (ratio_sma_ceil 1.30, low-vol gate, 反向假設驗證): Part A
    #   17/64.7%/0.16 cum +9.78% (max consec losses 4) / Part B 9/66.7%/
    #   0.21 cum +6.60% / min 0.16 REJECT (三次最差). CEILING 反向移除
    #   Part A winners; 確認 Volume / SMA20 比率在 raw 形式下對 COPX
    #   兩段皆無乾淨 selectivity.
    # Att3 ★ (zscore_60_floor 0.5, 60d 滾動 z-score 標準化):
    #   Part A 14/85.7%/Sharpe 0.82 cum +37.41% MDD -6.31% PF 4.53
    #     max consec losses 1 (vs COPX-007 baseline 21/76.2%/0.45,
    #     +82% Sharpe / +9.5pp WR / consec losses 2→1)
    #   Part B 6/83.3%/Sharpe 0.71 cum +13.26% MDD -8.71% PF 3.77
    #     max consec losses 1 (vs baseline 10/80%/0.57, +25% Sharpe /
    #     +3.3pp WR)
    #   min(A,B) 0.71 SUCCESS (vs COPX-011 跨框架最優 0.64, +11%;
    #     vs COPX-007 baseline 0.45, +58%)
    #   A/B annualized cum gap 11.4% ✓ (<30%)
    #   A/B annualized signal gap 6.7% ✓ (<50%)
    #
    # 核心發現 (repo first volume z-score 60d filter on commodity miners ETF):
    # 1. Volume z-score 60d 標準化解決 raw ratio_sma 兩段反向選擇問題 ——
    #    COPX ETF AUM 持續成長使 Volume 絕對量基線漂移, 純 ratio 比較在
    #    Part A (2019-2023, AUM 較小) vs Part B (2024-2025, AUM 較大) 下
    #    對應不同 z-score regime; 60d rolling baseline + std 自適應消除
    #    這個 regime 漂移效應.
    # 2. z-score >= 0.5 (約 0.5σ above recent mean) 為甜蜜點: 過濾掉
    #    Part A 7 SLs (含 2019-08-01, 2020-01-28, 2020-02-25 等 macro
    #    shock 連續 SLs) 同時保留 12 個 Part A winners + 5 個 Part B
    #    winners.
    # 3. 維度為 OHLC 之外的第四維度 + 與 ATR ratio (price range surge)
    #    正交 —— ATR ratio 1.05 過濾「慢磨下跌」(range 不擴張),
    #    Vol z-score 過濾「冷清恐慌」(無 institutional 參與), 兩維度
    #    疊加 surgical: Part A WR 76.2→85.7% (+9.5pp), max consec 2→1.
    # 4. 反向 lesson #6 (確認指標邊際效益遞減) 在「資產內生 OHLCV
    #    第四維度 + 時間自適應標準化」雙條件下: 確認指標可結構性提升,
    #    但 raw / non-normalized 形式仍會反向選擇 (Att1+Att2 已驗證).
    volume_filter_mode: str = "zscore_60_floor"
    volume_sma_period: int = 20
    volume_ratio_threshold: float = 1.30
    volume_zscore_period: int = 60
    volume_zscore_threshold: float = 0.5
    volume_cum_lookback: int = 5
    volume_cum_threshold: float = 1.20

    # 冷卻期 (沿用 COPX-007)
    cooldown_days: int = 12


def create_default_config() -> COPX018Config:
    return COPX018Config(
        name="copx_018_volume_confirmed_mr",
        experiment_id="COPX-018",
        display_name="COPX Volume-Confirmed Capitulation MR",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.045,
        holding_days=20,
    )
