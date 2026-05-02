"""
TLT TLT-SPY Cross-Asset Divergence Regime-Gated MR (TLT-014)

實驗動機：
- TLT-013 Att1 為當前全域最優（min(A,B) 0.14，Part A Sharpe 0.14 / Part B 0.65），
  但 A/B 累計差距 61% 結構性過大（Part A +3.53% vs Part B +9.07%），主要來自
  Part A 的 2 筆停損（2020-05-26 -3.6%、2021-02-04 -3.6%）共拖累 -7.2%。
- TLT-013 Att3 嘗試 prior-DD 過濾這 2 筆 SLs 失敗（誤刪 winners），cross_asset_lessons.md
  指出此類 reflation/risk-on regime SLs 需要 forward-looking 或跨資產維度的 regime gate。
- ^MOVE filter（TLT-013 Att1）為 forward-looking implied vol 維度，但無法區分
  reflation regime（rate up + equity up）vs flight-to-safety regime（rate up + equity down）。
- TLT-008 IEF pair（同 duration）+ TLT-009 ^TNX velocity（same-asset rate）已驗證
  與 TLT 同類資產或 same-driver 指標作為 regime gate 結構性受限。

嘗試方向（repo 首次：cross-asset divergence regime gate using SPY equity benchmark）：
**TLT vs SPY 多週期報酬差過濾**。
核心思想：
- 2 筆 Part A SLs（2020-05-26、2021-02-04）的共同特徵：SPY 在前 20 日大幅上漲
  （COVID 復甦/reflation rally）+ TLT 同期下跌（殖利率上升），TLT-SPY 20d
  return 差距嚴重負值（< -10%）。此為「reflation regime」結構性壓制 TLT MR。
- 健康的 TLT MR 訊號通常發生在：(a) flight-to-safety regime（兩者同跌或 TLT 平、
  SPY 跌）、(b) calm regime（兩者皆橫盤）、或 (c) duration-spread MR（TLT 短期
  超賣 + SPY 平穩）。這些情境 TLT - SPY 20d return 差距 >= -5%（即 TLT 不會比
  SPY 落後超過 5%）。
- TLT - SPY divergence 為 cross-asset regime classifier，與 ^MOVE forward-looking
  implied vol 在不同維度（cross-asset performance differential vs 隱含波動率），
  二者**正交**。

與 lesson #5「趨勢濾波器+均值回歸=災難」的區分：
- lesson #5：禁止「TLT 自身趨勢過濾」（如 Close > SMA(50)），因為 MR 本質是在
  下跌中買入，過濾下跌趨勢 = 過濾好訊號
- 本實驗：TLT-SPY divergence 是**跨資產 regime classifier**，過濾的不是 TLT 趨勢
  本身，而是「TLT 與 SPY 出現結構性背離」的 regime（reflation 或 risk-on transition），
  此 regime 中 TLT MR 結構性失效（與技術面 oversold 無關）

與 TLT-007 / TLT-013 的區分：
- TLT-007 BB-width = TLT 自身 backward-looking realized vol gate
- TLT-013 ^MOVE = bond options forward-looking implied vol gate
- TLT-014 TLT-SPY divergence = cross-asset performance differential regime gate
- 三者理論上獨立作用，分別捕捉「TLT 自身波動」「bond market 預期」「跨資產 regime」

迭代計畫：
- Att1：TLT 20d return - SPY 20d return >= -5% 過濾，疊加於 TLT-013 Att1 全部條件
- Att2：根據 Att1 結果調整 lookback 或閾值（10d/-3%、30d/-7%）
- Att3：探索替代維度（TLT vs LQD 投資級債券）或不同 SPY threshold
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT014Config(ExperimentConfig):
    """TLT-014 TLT-SPY Cross-Asset Divergence Regime-Gated MR 參數

    迭代紀錄：
      Att1 (min_relative_return=-0.05, divergence_lookback=20)：
        Part A 7/71.4%/Sharpe **0.32** cum +5.29% / Part B 4/100% WR std=0 cum +10.38% /
        min(A,B) **0.32**（+129% vs TLT-013 Att1 0.14）。2 個原始 Part A SLs
        （2020-05-26、2021-02-04）皆被過濾，但 cooldown chain shift 引入 2021-02-08 新 SL。
        A/B cum 差 49% > 30% ❌（從 61% 改善但未達標），訊號比 7:4 = 43% < 50% ✓

      Att2 (min_relative_return=-0.03 加嚴)：
        TBD：執行回測後填寫結果。
    """

    # 回檔範圍進場（同 TLT-013 Att1）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-013 Att1）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-013 Att1）
    close_position_threshold: float = 0.4

    # BB-width regime gate（同 TLT-013 Att1）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # ^MOVE forward-looking implied vol regime gate（同 TLT-013 Att1）
    move_ticker: str = "^MOVE"
    max_move_level: float = 130.0

    # TLT-SPY cross-asset divergence regime gate（TLT-014 核心新增）
    benchmark_ticker: str = "SPY"
    divergence_lookback: int = 20  # N 日報酬差距
    # min_relative_return：TLT N 日報酬 - 基準 N 日報酬 必須 >= 此值
    # 即「TLT 不可比 SPY 落後超過 |min_relative_return|」
    min_relative_return: float = -0.03

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT014Config:
    return TLT014Config(
        name="tlt_014_tlt_spy_divergence_mr",
        experiment_id="TLT-014",
        display_name="TLT TLT-SPY Cross-Asset Divergence Regime-Gated MR",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,
        stop_loss=-0.035,
        holding_days=20,
    )
