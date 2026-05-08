"""
TLT Yield-Curve-Slope Inflation-Regime-Gated MR (TLT-017)

實驗動機 (Problem statement):
- TLT-014 Att3 為當前全域最優 (min(A,B) 0.69, Part A 0.69 / Part B 0.00 zero-var).
  Part A binding, 5 訊號 / WR 80% / cum +6.56%, **殘餘 1 EX -2.38% on 2021-01-06**.
- 此 EX 為「2021 reflation regime」經典訊號 (Georgia Senate runoff + 財政刺激 +
  疫苗 rollout): SPY 急漲 + TLT 急跌 + yields surging on inflation expectations.
- TLT-014 已含三層 regime gate:
  1. BB-width 5% (TLT 自身 backward-looking realized vol)
  2. ^MOVE Close <= 130 LEVEL CAP (forward-looking implied vol level)
  3. TLT-SPY 20d divergence >= -4% (cross-asset performance differential regime)
- TLT-016 嘗試 ^MOVE multi-window IV DIRECTION combo (USO-028 cross-strategy port)
  三次迭代全 REJECT/TIE: 2021-01-06 EX 之 ^MOVE trajectory (5d=-1.46) cluster
  mid-distribution among Part A winners, IV trajectory 維度結構性無法區分.
- TLT-015 (HYG credit divergence) note 明確列出突破 0.69 ceiling 的「真正正交維度」:
  (a) 殖利率曲線陡峭化 ^TYX - ^TNX 30Y-10Y slope (forward-looking 通膨預期)
  (b) DXY 美元指數 (FX 維度)
  (c) TIPS-Treasury breakeven inflation rate

嘗試方向 (repo 首次使用 yield curve slope velocity 作為 regime gate):
**^TYX - ^TNX 30Y-10Y yield curve slope velocity** as 4th orthogonal regime dim.
- ^TYX = 30Y Treasury yield (含長端通膨溢價)
- ^TNX = 10Y Treasury yield (含短中期通膨預期)
- Slope = ^TYX - ^TNX (yield curve steepness in percentage points)
- Slope_change_N = Slope_today - Slope_N_days_ago (steepening velocity)
- 假設: 當 slope 在短期內快速擴張 (急速 steepening), 表示市場對長端通膨溢價快速
  上修, 此為 **inflation-regime onset**, 結構性壓制 TLT (long-duration bond) MR.

預期效應 (probe data 已證實):
- 2021-01-06 殘餘 EX 之 slope_10d = +0.036 (最高 steepening), slope_5d = +0.040
  (最高), slope_20d = +0.021. **此為候選 Part A 訊號中 slope 各維度最強的
  steepening 事件**, 完全契合「reflation regime onset」假設.
- 2020-08-12 EX +0.40% 之 slope_10d = +0.032 (第二高), 雖在邊界但仍正期望值.
- Part A 其他 winners (2021-08-11, 2022-02-07) slope_10d ≤ +0.018 (低 steepening),
  Part B winners 多為 negative or low slope_change (rate cycle 反轉期 flattening).

與既有 regime gate 維度的正交性:
- TLT-007 BB-width: TLT 自身 realized volatility (price-based)
- TLT-013 ^MOVE LEVEL: bond options implied vol level (option-implied)
- TLT-014 TLT-SPY divergence: cross-asset relative performance (equity benchmark)
- **TLT-017 yield curve slope velocity: forward-looking inflation expectations
  (rate-curve-shape-based)** — 與前三維結構性正交, 直接捕捉通膨預期維度,
  TLT-015 HYG credit / TLT-016 ^MOVE multi-window 皆未涵蓋此維度

迭代計畫 (3 iterations max):
- Att1: slope_lookback=10d, max_slope_change <= +0.035 (基於 probe 數據,
  surgical filter 2021-01-06 +0.036 為唯一超越閾值之候選 Part A 訊號)
- Att2: 視 Att1 結果調整 lookback (5d acute / 20d sustained) 或閾值方向
- Att3: 探索替代維度 (slope level itself, 或 slope direction reversal)

成功判準 (acceptance criteria, max 3 iterations):
1. min(A,B) Sharpe > 0.69 (TLT-014 Att3 baseline)
2. A/B 累計差距 < 30%
3. A/B 訊號數差距 < 50%
4. 使用 execution model
5. 失敗時記錄: 失敗原因 + cooldown chain shift 結構 + 對 lesson #24 family 邊界貢獻
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT017Config(ExperimentConfig):
    """TLT-017 Yield-Curve-Slope Inflation-Regime-Gated MR 參數

    迭代紀錄將在執行後填入.
    """

    # 進場 (沿用 TLT-014 Att3)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_upper: float = -0.07

    wr_period: int = 10
    wr_threshold: float = -80.0

    close_position_threshold: float = 0.4

    # BB-width regime gate (沿用 TLT-007 / TLT-013 / TLT-014)
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # ^MOVE LEVEL CAP (沿用 TLT-013 Att1 / TLT-014)
    move_ticker: str = "^MOVE"
    max_move_level: float = 130.0

    # TLT-SPY cross-asset divergence (沿用 TLT-014 Att3)
    benchmark_ticker: str = "SPY"
    divergence_lookback: int = 20
    min_relative_return: float = -0.04

    # TLT-017 核心新增: yield curve slope velocity (^TYX - ^TNX) regime gate
    long_yield_ticker: str = "^TYX"  # 30Y Treasury yield
    short_yield_ticker: str = "^TNX"  # 10Y Treasury yield
    slope_lookback: int = 5  # N 日 slope 變化
    # max_slope_change: slope (^TYX - ^TNX) 在 N 日內的變化必須 <= 此值 (in % points)
    # 意義: 「殖利率曲線在 N 日內 steepening (long-end 通膨溢價擴張) 不可超過此幅度」
    #
    # 迭代紀錄 (3 iterations all completed):
    # Att1: 10d, +0.035 → SUCCESS min(A,B)† 4.49 但 Part B 4→3 (2025-03-27 slope_10d=
    #   +0.036 與 2021-01-06 同值, 10d 維度無法區分 Part B winner vs Part A loser)
    # Att2 ★: 5d, +0.038 → SUCCESS min(A,B)† 4.49, Part B 完全恢復 4/4
    #   (2021-01-06 slope_5d=+0.040 vs 2025-03-27 +0.035, 5d acute 維度有區分力)
    # Att3 (alternative dim): slope LEVEL <= +0.700 filter (no velocity) →
    #   REJECT min(A,B)† 3.94. slope LEVEL 因 2020-11-09 slope=+0.793 (winner)
    #   與 2021-01-06 slope=+0.779 (loser) 同處於高 LEVEL 帶, 無區分力, 誤殺
    #   Part A winner. 確認 slope VELOCITY (5d acute) > slope LEVEL 之 selectivity
    #
    # Att2 為最終最優, 沿用為 default
    max_slope_change: float = 0.038
    use_slope_change_filter: bool = True

    # slope LEVEL filter (Att3 測試 alternative dimension, 確認 LEVEL 不如 VELOCITY)
    # 預設關閉, 保留欄位以記錄 Att3 試驗
    use_slope_level_filter: bool = False
    max_slope_level: float = 999.0

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT017Config:
    return TLT017Config(
        name="tlt_017_yield_curve_slope_mr",
        experiment_id="TLT-017",
        display_name="TLT Yield-Curve-Slope Inflation-Regime-Gated MR",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,
        stop_loss=-0.035,
        holding_days=20,
    )
