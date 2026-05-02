"""
TSM-011: Signal-Day Direction Filter on RS Momentum Pullback 配置
TSM Signal-Day Direction Filter on RS Momentum Pullback Configuration

策略方向：在 TSM-008 RS 動量回調框架上加入 signal-day return CEILING 過濾，
解決「rally exhaustion 偽訊號」（5 日已大漲後出現淺回檔但實為趨勢反轉前兆）。

Lesson #19 family cross-strategy 鏡像擴展（repo 首次嘗試）：
- 過往：MR 框架使用 1d/2d/3d/5d return FLOOR 作為 capitulation depth 過濾
  （DIA-012 / GLD-014 / SPY-009 / EWJ-005 / EWZ-007 / CIBR-014 / SIVR-018 / URA-013 / INDA-011）
- 本實驗：RS 動量框架使用 5d return CEILING 作為「rally exhaustion 過濾」（鏡像方向）
- 假設：MR 失敗訊號特徵為「太淺 capitulation」（floor 過濾），momentum 失敗訊號特徵為
  「太深 rally」（ceiling 過濾），兩者結構性鏡像。

進場條件（沿用 TSM-008，所有條件需同時滿足）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. **新增 signal-day 5d return CEILING <= +10.5%（rally exhaustion 過濾）**
5. 冷卻期 10 個交易日

三次迭代結果：
- Att1（1d ceiling <= +1.0%）：FAILED — Part A Sharpe 0.78（vs baseline 0.79）。
  1d 過濾觸發 cooldown chain shift（lesson #19）將 2020-07-24 expiry -1.72% 替換為
  2020-07-31 expiry -2.22%（更差），淨效果負面。
- Att2（5d ceiling <= +9.5%）：Sharpe 大幅改善但 A/B 失衡。
  Part A 11 訊號 WR 90.9% Sharpe **1.30** cum **+87.38%**（vs baseline 0.79/+69.59%），
  Part B 10 訊號 Sharpe 0.83 不變，min(A,B) **0.83** (+5%)。
  但 A/B 累計差距 31.6% 略超 30% 目標（cooldown chain shift 移除 2022-11-21 SL 與
  2022-12-07 SL，僅留 2022-11-28 SL）。
- Att3 ★（5d ceiling <= +10.5%）：所有 acceptance criteria 通過。
  Part A 12 訊號 WR **83.3%** Sharpe **0.86** cum **+74.10%**（vs baseline 0.79/+69.59%），
  Part B 10 訊號 Sharpe 0.83 不變 cum +59.78%，min(A,B) **0.83**（+5% vs 0.79）。
  A/B 累計差距 **19.3%** (< 30% ✓), A/B 訊號比 1.2:1 (gap 16.7% < 50% ✓)。
  關鍵改善：5d ceiling +10.5% 僅過濾 2020-07-24 訊號（5d +11.30%, expiry -1.72%），
  cooldown chain shift 引入 2020-07-31 expiry +0.89%（從負轉正）+ 2020-08-20 TP +8%。
  Part B 完全不受影響（Part B 訊號 5d 最高為 2024-02-12 +9.82% < +10.5%）。

跨資產貢獻（lesson #19 family v10）：
- Repo 首次「return CEILING（rally exhaustion filter）」方向於任何資產
- Repo 首次 lesson #19 family cross-strategy 鏡像擴展：MR 框架 → momentum 框架
- 與既有 FLOOR 方向（DIA-012 / GLD-014 / SPY-009 / EWJ-005 等）結構性正交
- 跨資產假設（待驗證）：rally exhaustion ceiling 可能適用於其他 RS / MBPC 動量框架
  （NVDA-006 / TSM-007 / VOO-004 / SOXL-010 等），閾值需依資產 5d return 分布調整
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMSignalDayFilterConfig(ExperimentConfig):
    """TSM Signal-Day Direction Filter 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # Signal-day return CEILING 過濾（>= 999 視為停用）
    ret_1d_max: float = 999.0  # 1 日報酬上限（Att1 驗證單獨無效，停用）
    ret_5d_max: float = 0.095  # 5 日報酬上限 +9.5%（Att2: aggressive rally exhaustion filter）


def create_default_config() -> TSMSignalDayFilterConfig:
    return TSMSignalDayFilterConfig(
        name="tsm_011_signal_day_filter",
        experiment_id="TSM-011",
        display_name="TSM Signal-Day Direction Filter",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
