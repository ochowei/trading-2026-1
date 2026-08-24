"""
TSM-017: Earnings-Date Exclusion Filter on RS Momentum Pullback 配置
TSM Earnings-Date Exclusion Filter on RS Momentum Pullback Configuration

策略方向：在 TSM-011 Att3 的 RS Momentum Pullback 框架上加入
**Earnings-Date Exclusion Filter**，排除 TSM 季報前後 N 日的進場訊號。

假設來源（TSM-016 Att3 失敗報告 + AI_CONTEXT 列出之未驗證方向）：
- TSM-016 Att3 確認 earnings-week 為高 SL 風險區間：「0.14 閾值同時放回
  cooldown chain 觸發的 earnings-week SLs（2024-10-16 T-1 to earnings 10/17、
  2025-01-16 同日 earnings、2024-11-01 chain shift）」
- TSM-011 Att3 baseline Part B 殘餘 SLs：
  - 2024-07-16 SL: TSM Q2 2024 earnings = 2024-07-18，2 日前
  - 2024-10-30 SL: TSM Q3 2024 earnings = 2024-10-17，13 日後
- TSM AI_CONTEXT 明確列出「earnings-date exclusion filter」為待驗證未嘗試方向

Lesson #6 邊界（不同類型）：
- 過往 TSM 失敗多為「signal-day filter」（5d ceiling / volume / Rel_QQQ），TSM-017
  改用「日期型 calendar filter」——時間維度而非價格/成交量維度，與既有失敗類別正交。
- 跨資產罕見：repo 首次 earnings-date exclusion filter 於任何資產。

進場條件（沿用 TSM-011 Att3，新增第 6 條件）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 訊號日 5 日報酬 <= +10.5%（rally exhaustion 過濾）
5. **新增：訊號日不在 TSM earnings ± exclusion window 內**
6. 冷卻期 10 個交易日

三次迭代結果（基線 TSM-011 Att3 min(A,B) Sharpe 0.83）：
- Att1（asymmetric -10/+15 calendar days，25 日總窗口）：FAILED min(A,B) **0.42** REJECT。
  Part A 7 訊號 71.4% WR Sharpe 0.42 cum +19.28%（vs baseline 12/83.3%/0.86/+74.10%，
  Part A -51% Sharpe）/ Part B 6 訊號 83.3% WR Sharpe **0.98** cum +36.52%
  （vs baseline 10/80%/0.83/+59.78%，Part B +18% Sharpe）。Window 過寬切除 5 個 Part A
  訊號，cum -73% 嚴重退化。
- Att2（bilateral ±5 calendar days，11 日窗口）：FAILED min(A,B) **0.71** REJECT。
  Part A 10 訊號 80% WR Sharpe 0.71 cum +49.26%（-17% vs baseline 0.86）/
  Part B 7 訊號 **85.7% WR** Sharpe **1.11** cum +47.44%（**+34% vs baseline 0.83**）。
  Part B 突破，但 cooldown chain shift 將 2024-10-30 SL 替換為 2024-10-23 SL（同樣 SL）;
  另 2024-07-16 SL 過濾後激活 2024-06-27 TP（淨 +1 winner）。Part A 損失 2 訊號。
- Att3（bilateral ±2 calendar days，5 日窗口，最緊邊界）：FAILED min(A,B) **0.78** REJECT。
  Part A 11 訊號 81.8% WR Sharpe 0.78 cum +61.20%（-9% vs baseline 0.86）/
  Part B 7 訊號 85.7% WR Sharpe 1.11 cum +47.44%（同 Att2，+34% vs baseline）。
  Part A 僅損失 1 訊號（最佳保留）但 Sharpe 仍退化；A/B 年化幾何 cum 差 |10.0%-21.4%| /
  21.4% = **53% > 30% target ❌**（Part B 受限於 2 年 sample 高度集中於 2024-2025
  bull regime 使年化稀釋）。

核心失敗發現（lesson #20b 失敗家族擴展，repo 首次 earnings-date exclusion filter 於任何資產）：
1. **時間維度 filter 與價格/成交量 filter 正交但仍受日期重疊限制**——TSM Part B 殘餘
   SLs（2024-07-16 -2d / 2024-10-30 +13d）與 winners（2024-04-16 -2d / 2025-01-13 -3d /
   2023-01-19 +7d）在 earnings-relative 日期維度結構性重疊，**不存在單一窗口配置同時
   過濾全部 SLs 並保留全部 winners**：
   - 對稱 ±2: 過濾 2024-07-16 SL ✓ 與 2024-04-16 winner ✗（1:1 wash）
   - 對稱 ±5: 同上 + 觸發 cooldown chain shift 引入 2024-10-23 SL（淨 wash）
   - 非對稱 -2/+14: 過濾兩 SLs ✓ 但同時誤殺 2024-04-16 winner ✗ + 2023-01-19 winner ✗（2:2 wash）
   - 後置 only +14: 過濾 2024-10-30 SL ✓ 但誤殺 2023-01-19 winner ✗（1:1 wash）
2. **Part A 退化機制**：Part A 包含多個 earnings-adjacent winners（2020-2023 期間
   半導體 cycle 拉抬 + earnings momentum continuation），任何時間窗口擴大皆切除 Part A
   winners 多於 Part A SLs（baseline Part A 只有 2 SLs，2022-11-21 / 2022-12-07
   均不在 earnings 附近）。
3. **Part B 改善 +34% 為「earnings-week SL cluster」確認**——TSM-016 Att3 假設成立：
   Part B SLs 集中於 earnings ±15 日帶；但同時 Part B winners（2024-04-16 / 2025-01-13）
   亦集中於 earnings 前 2-3 日，**winner/SL 在時間維度為共生分布**而非可分離 cluster。
4. **新跨資產規則（lesson #6 邊界 + lesson #20b 擴展）**：
   - earnings-date exclusion filter 適用邊界 = 「target 之 earnings-adjacent 訊號分布
     winner-SL 比例顯著高於 non-earnings 訊號分布」
   - TSM 違反該條件：earnings-adjacent 期間 winner-SL 比例與 non-earnings 期間相近
     （半導體個股 earnings momentum 與 earnings risk 兩股力量平衡）
   - 預期適用候選：fundamentals-driven 個股（financial / consumer / healthcare），
     earnings 為 dominant catalyst 使 winner/SL 比例顯著偏移；不適用於：cyclical
     individual stocks（半導體 / energy / commodity）earnings 為次要 catalyst
5. **TSM Part B 0.83 binding constraint 第 5 次結構性無解確認**——TSM-013 (QQQ CEILING) +
   TSM-014 (QQQ BAND) + TSM-015 (AAPL anchor) + TSM-016 (BB-Width regime gate) +
   TSM-017 (earnings exclusion) 共五次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產。
   未來方向應為 (a) SOXX 半導體指數 anchor（注意 TSM 為成分股自我參考）,
   (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting),
   (c) 完全替代 framework（lesson #22 multi-week regime + RS Momentum 組合），
   (d) Volatility-Acceleration BAND filter（CIBR-014/FXI-014 路徑）。

成交模型參數：滑價 0.1%、TP +8.0%、SL -7.0%、最長持倉 25 天、冷卻 10 天。
"""

from dataclasses import dataclass, field

from trading.core.base_config import ExperimentConfig

# TSM (Taiwan Semiconductor) historical quarterly earnings announcement dates.
# Source: public earnings releases. Dates are calendar dates (not necessarily
# trading days) and represent the announcement day.
TSM_EARNINGS_DATES: tuple[str, ...] = (
    "2018-04-19",
    "2018-07-19",
    "2018-10-18",
    "2019-01-17",
    "2019-04-18",
    "2019-07-18",
    "2019-10-17",
    "2020-01-16",
    "2020-04-16",
    "2020-07-16",
    "2020-10-15",
    "2021-01-14",
    "2021-04-15",
    "2021-07-15",
    "2021-10-14",
    "2022-01-13",
    "2022-04-14",
    "2022-07-14",
    "2022-10-13",
    "2023-01-12",
    "2023-04-20",
    "2023-07-20",
    "2023-10-19",
    "2024-01-18",
    "2024-04-18",
    "2024-07-18",
    "2024-10-17",
    "2025-01-16",
    "2025-04-17",
    "2025-07-17",
    "2025-10-16",
    "2026-01-15",
    "2026-04-16",
)


@dataclass
class TSMEarningsExclusionConfig(ExperimentConfig):
    """TSM Earnings-Date Exclusion Filter 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # 沿用 TSM-011 Att3 的 5d return CEILING（rally exhaustion）
    ret_5d_max: float = 0.105

    # Earnings-Date Exclusion Filter（calendar days，非交易日）
    earnings_dates: tuple[str, ...] = field(default_factory=lambda: TSM_EARNINGS_DATES)
    # Att3 最終配置（最緊邊界 ±2 calendar days，三次迭代中 min 最佳）
    earnings_pre_days: int = 2  # earnings 前 N 日排除（含 N=0 即當日）
    earnings_post_days: int = 2  # earnings 後 N 日排除（含 N=0 即當日）


def create_default_config() -> TSMEarningsExclusionConfig:
    return TSMEarningsExclusionConfig(
        name="tsm_017_earnings_exclusion",
        experiment_id="TSM-017",
        display_name="TSM Earnings-Date Exclusion Filter on RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
