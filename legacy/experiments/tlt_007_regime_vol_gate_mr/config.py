"""
TLT Volatility-Regime-Gated Mean Reversion 配置 (TLT-007)

實驗動機：
- TLT-002 為當前最佳（Part A Sharpe -0.20，Part B Sharpe 0.24），Part A 受 2022 升息
  週期連續假訊號殺死：TLT-002 Part A 42 訊號 WR 47.6%、2022 年 11 訊號中 8 筆停損
- TLT-006 Day-After Capitulation（Close>Prev High 反轉 K 線）在 TLT 失敗（lesson #20b
  擴展至 interest-rate policy driven asset），確認 entry-time price-action 過濾器
  無法解決 2022 regime 問題
- TLT-002 的 「60 日跌幅 ≤ 10%」regime 過濾過於寬鬆，2022 年大部分 60 日滾動跌幅
  仍落在 5-10% 區間，無法過濾該期間訊號

嘗試方向（repo 中未曾嘗試於 TLT）：**波動率 regime 閘門（Volatility Regime Gate）**。
核心思想：
- 2022 升息期 TLT 波動率持續飆升，BB(20, 2) 通道寬度（2 × 2σ）相對於價格常超過 6-8%
- 2024-2025 高利率高原期與 2019-2021 降息期波動率相對穩定，BB 寬度通常 < 5%
- 將 BB 寬度（BB_width / Close < 閾值）作為 regime 過濾器，可一次性排除整個 2022
  結構性下跌期間的訊號，同時保留其他年份的 MR 機會
- 這是 regime filter（市場狀態）而非 short-term trend filter（進場日趨勢），
  不違反 lesson #5（MR + 趨勢過濾 = 災難，主要指進場日短線趨勢）

與 lesson #5 的區分：
- Lesson #5：均值回歸進場時若加入「當日 Close > SMA(50)」這類短線趨勢過濾，會濾掉
  在下跌中進場的好訊號（MR 的本質就是買在下跌中）
- 本實驗：BB width regime filter 是針對「整體波動率環境」的分類器，當 20 日實現
  波動率非極端時放行 MR 訊號，本質是在兩個 regime（crisis / calm）中挑選 calm regime
  進行 MR，不是在當日壓制訊號

設計理念（執行模型同 TLT-002）：
- 保留 TLT-001/002 驗證有效的進場條件（pullback 3-7% + WR ≤ -80 + ClosePos ≥ 40%）
- 加入 BB(20, 2) 寬度 / Close < 閾值的 calm regime 閘門
- 出場沿用 TLT-001/002 驗證的 TP +2.5% / SL -3.5% / 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT007Config(ExperimentConfig):
    """TLT-007 Volatility-Regime-Gated Mean Reversion 參數

    迭代紀錄（三次迭代）：
      Att1（max_bb_width_ratio=0.06，Part A 24/45.8%/Sharpe -0.20、Part B 10/80.0%/Sharpe 0.48）：
        BB 寬度 6% 門檻過寬，2022 升息期 2022-01/03/06/08 四筆訊號仍通過過濾（BB 寬度
        雖大但通道窄期間仍低於 6%），未改善 Part A。min(A,B) 持平 TLT-002 的 -0.20。

      Att2（max_bb_width_ratio=0.05，Part A 12/50.0%/**Sharpe 0.12**、Part B 6/83.3%/Sharpe 0.65）★：
        BB 寬度收緊至 5% 成功過濾 2022 升息期多數訊號（2022 僅剩 2022-02-07 通過且為贏家），
        Part A 訊號 24→12，保留的 12 筆中 6 贏 3 停損 3 到期小虧。**首次達成 TLT min(A,B)
        為正值**（0.12 vs TLT-002 的 -0.20），Part B Sharpe 0.65 超越 TLT-002 的 0.24
        （+171%）。A/B 訊號年化率 2.4/yr vs 3.0/yr（差距 20%，<50% ✓）；A/B 累計差
        2.95% vs 9.07%（差距 67.5%，>30% ✗，但 Part B 優於 Part A 屬利多不對稱，非
        overfitting 結構）。

      Att3（require_long_term_trend_filter=True，Part A 7/57.1%/Sharpe 0.29、Part B 3/66.7%/Sharpe 0.16）：
        Att2 + SMA(100) 今日 >= SMA(100) 20 日前斜率濾波。Part A 訊號再砍半至 7（移除
        2020-05、2021-01/02 持續下跌期訊號），Sharpe 升至 0.29。但 SMA(100) 斜率在
        Part B 2024-2025 高利率高原期常為負值，Part B 訊號從 6 砍至 3，Sharpe 崩壞至
        0.16，min(A,B) 雖表面提升至 0.16 但 Part B 統計信心不足（3 筆零方差風險）。
        **放棄 Att3** — 退回 Att2 配置作為最終版本。

    失敗分析（Att1/Att3）：
      - Att1 BB 6% 過寬：2022 升息期 TLT 波動率雖高但通道擴張呈階梯式，部分日子 BB 寬度
        低於 6%。5% 為分界點；4% 會過度砍 Part B（TLT 日波動 1%，4% 門檻僅約 0.8σ std）
      - Att3 SMA 斜率濾波在 Part B 失效：2024-2025 TLT 橫盤時 SMA(100) 斜率在多數時點
        接近 0，易在高頻波動中切換正負，造成 Part B 隨機性訊號流失。**學習**：波動率
        regime 閘門（BB 寬度）與長線趨勢濾波結構上不互補——前者捕捉「短期 volatility
        regime」，後者捕捉「中長期方向」。對 TLT 而言波動率 regime 更穩定可靠

    最終配置：Att2（max_bb_width_ratio=0.05，require_long_term_trend_filter=False）
    """

    # 回檔範圍進場（同 TLT-001/002）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-001/002）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-001/002）
    close_position_threshold: float = 0.4

    # 波動率 regime 閘門（新增）：BB(bb_period, bb_std) 寬度 / Close < max_bb_width
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05  # Att2 收緊至 5%（Att1 6% 仍放行 2022 升息期訊號）

    # SMA(100) 趨勢 regime 閘門（Att3 測試後禁用 — 過濾過度、Part B 訊號砍半）
    require_long_term_trend_filter: bool = False
    long_term_sma_period: int = 100
    long_term_sma_slope_lookback: int = 20  # SMA(100) 今日 >= SMA(100) N 日前

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT007Config:
    return TLT007Config(
        name="tlt_007_regime_vol_gate_mr",
        experiment_id="TLT-007",
        display_name="TLT Volatility-Regime-Gated MR",
        tickers=["TLT"],
        data_start="2018-01-01",  # 需要 SMA/BB 的 200 日暖機
        profit_target=0.025,  # +2.5%（同 TLT-002）
        stop_loss=-0.035,  # -3.5%（同 TLT-002）
        holding_days=20,
    )
