"""
COPX Yield-Curve-Slope Industrial-Demand-Regime-Gated MR (COPX-017)

實驗動機 (Problem statement):
- COPX 全域最優為 COPX-011 Att3 BB Squeeze Breakout 框架 min(A,B) 0.64,
  Part B 僅 2 訊號為結構性 sample size binding constraint, 任何 filter 對 Part B
  非綁定皆使 min 結構性 TIE.
- COPX-007 Vol-Adaptive MR 框架擁有更多 Part B 訊號 (10 訊號, Part A 21 訊號)
  Part A Sharpe 0.45 / Part B Sharpe 0.57 / min 0.45, 為更穩健的 baseline 起點.
- 既有 COPX cross-asset macro filters 試驗:
  * COPX-013 (Macro-Confirmed: SPY 10d gate) FAIL: SPY 10d 維度 winners/SLs 重疊
  * COPX-014 (GLD divergence on Breakout) FAIL: cooldown chain shift collapse
  * COPX-015 (^VIX FLOOR on Breakout) PARTIAL: Part A 大幅改善但 Part B 非綁定
  * COPX-016 (DXY direction on Breakout) PARTIAL: 同 COPX-015, Part B 非綁定
- 全部既有 cross-asset macro filters 皆 build on Breakout (BB Squeeze) 框架.
  **MR 框架尚未疊加任何 cross-asset macro regime gate**.

嘗試方向 (repo 首次 yield curve slope velocity 移植至商品/礦業 ETF):
**(^TYX - ^TNX) 30Y-10Y yield curve slope velocity** as cross-asset macro
regime gate, 套用於 COPX-007 vol-adaptive MR 框架.
- ^TYX = 30Y Treasury yield (含長端通膨/成長預期)
- ^TNX = 10Y Treasury yield (含短中期 rate path 預期)
- Slope = ^TYX - ^TNX (yield curve steepness, 正值為正常 steepening)
- Slope_change_N = Slope_today - Slope_N_days_ago

假設 (industrial demand regime hypothesis):
- 對工業金屬 ETF (COPX, "Dr. Copper" miners), yield curve slope 反映:
  * 急速 steepening (slope_change > 0): 反通膨 / 成長預期上升 = 工業需求預期改善
  * 急速 flattening (slope_change << 0): 衰退預期升溫 = 工業需求預期惡化
- COPX 殘餘 SL 多發生於 macro shock 期 (2019 Q1 trade war, 2020 COVID, 2022 Fed
  hike, 2023 China weakness, 2024 metals weakness), 多伴隨 risk-off + 殖利率
  曲線快速 flattening 反映 recession fear escalation.
- 假設: 過濾掉「殖利率曲線在 N 日內快速 flattening 超過閾值」的 MR 訊號,
  可改善 Part A 品質 (移除 macro-shock-aligned SLs) 而 Part B 因 2024-2025
  reflation regime 較少 flattening 而非綁定或受惠.

預期方向 (FLOOR direction, 對應 TLT-017 CAP direction 鏡像):
- TLT-017 (long bond MR): cap slope_change <= +0.038 (skip rapid steepening
  = inflation regime onset, structurally bad for long bonds)
- COPX-017 (commodity miner MR): floor slope_change >= -X (skip rapid
  flattening = recession regime onset, structurally bad for commodities)
- 對稱方向反映「資產 vs 殖利率曲線 slope 的結構性耦合方向」之差異

正交性 (orthogonality):
- COPX-007 既有維度: pullback (price) + WR (oscillator) + ATR ratio (vol)
- COPX-017 新增維度: forward-looking macro inflation/recession expectation
  (rate-curve-shape-based) — 與既有三維結構性正交

迭代計畫 (3 iterations max):
- Att1: slope_lookback=5d, min_slope_change >= -0.05 (loose floor, ~5bp 5-day
  flattening 上限)
- Att2: 視 Att1 結果調整 lookback (10d sustained / 20d secular) 或閾值嚴緊度
- Att3: 探索替代維度 (slope LEVEL itself, 或反向 mode 測試)

成功判準 (acceptance criteria):
1. min(A,B) Sharpe > 0.64 (COPX 跨框架全域最優, COPX-011 Att3 BB Squeeze)
2. A/B 累計差距 < 30% (COPX-011 baseline 已失敗此項, MR 框架更具改善空間)
3. A/B 訊號數差距 < 50%
4. 使用 execution model (繼承 ExecutionModelStrategy)
5. 失敗時記錄: 失敗原因 + cooldown chain shift 結構 + 對 lesson #24 family +
   lesson #25 family 邊界貢獻
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX017Config(ExperimentConfig):
    """COPX-017 Yield-Curve-Slope Industrial-Demand-Regime-Gated MR 參數

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

    # COPX-017 核心新增: yield curve slope velocity (^TYX - ^TNX) regime gate
    long_yield_ticker: str = "^TYX"  # 30Y Treasury yield
    short_yield_ticker: str = "^TNX"  # 10Y Treasury yield
    slope_lookback: int = 10  # N 日 slope 變化
    # min_slope_change: slope (^TYX - ^TNX) N 日內變化必須 >= 此值 (in % points)
    # 意義: 「殖利率曲線在 N 日內 flattening 不可超過此幅度 (絕對值)」
    # 直觀: -0.05 表示「不可在 N 日內 flattening 超過 5bp」
    #
    # 迭代紀錄 (3 iterations all REJECT vs COPX-007 MR baseline 0.45 + 跨框架
    # best COPX-011 BB Squeeze 0.64):
    # Att1 (5d, >= -0.05): Part A 19/73.7%/0.38 cum +27.64% / Part B 10/80%/0.57
    #   不變 / min 0.38 REJECT (vs COPX-007 baseline 0.45). Filter 移除 2 個
    #   Part A 訊號但 Sharpe 退化, reverse-selecting 結構.
    # Att2 (10d, >= -0.05): Part A 16/75%/0.42 cum +24.95% / Part B 不變 /
    #   min 0.42 REJECT (vs baseline 0.45). 10d lookback 移除 5 個 Part A 訊號,
    #   WR 微升 +1.3pp 但 cum -2.69%, winners 占比偏多 (高 cum 訊號被移除).
    # Att3 (slope LEVEL, min_slope_level >= 0.0 skip inverted curve):
    #   Part A 20/75%/0.42 cum +32.11% / Part B 不變 / min 0.42 REJECT.
    #   slope LEVEL 維度僅過濾 1 訊號 (21→20), 多數 COPX 訊號發生於正常曲線
    #   regime (slope > 0), filter 邊際收益接近零, 仍移除 winner 而非 loser.
    min_slope_change: float = -0.05
    use_slope_change_filter: bool = False  # Att3: disable velocity filter

    # slope LEVEL filter (Att3 alternative dimension, 啟用)
    # min_slope_level >= 0.0: 過濾倒掛曲線 (^TYX < ^TNX, slope < 0) 區間訊號
    # 假設: 倒掛曲線 = 衰退預期主導, COPX MR 在此區間為「持續探底」非「反彈起點」
    use_slope_level_filter: bool = True
    min_slope_level: float = 0.0

    # 冷卻期 (沿用 COPX-007)
    cooldown_days: int = 12


def create_default_config() -> COPX017Config:
    return COPX017Config(
        name="copx_017_yield_curve_slope_mr",
        experiment_id="COPX-017",
        display_name="COPX Yield-Curve-Slope Industrial-Demand-Regime-Gated MR",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.045,
        holding_days=20,
    )
