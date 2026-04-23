"""
TQQQ-017：恐慌抄底 + 盤中/加速確認 (Capitulation + Intraday/Acceleration Confirmation)

動機（Motivation）：
    TQQQ-010（當前最佳）在 Part A 出現 6 筆停損（20 訊號中，WR 70%，
    Sharpe 0.36），拖累 min(A,B) 從 Part B 的 1.02 降至 0.36。
    Part A 停損日期：2020-02-24、2020-03-12、2021-09-28、2022-03-08、
    2022-09-01、2022-09-21。觀察這些日子的共同特徵與勝利日的差異，設計
    篩選器以過濾「持續性下跌中的偽訊號」但保留「急速恐慌後的真反轉」。

策略方向：均值回歸（加入日內/加速過濾）

迭代歷程（Iteration Log）：

Att1 — ClosePos >= 0.30（日內反轉確認）【失敗】
    進場：20d DD <= -15% + RSI(5)<25 + Volume>1.5x SMA20 + ClosePos>=0.30
    結果：Part A n=11, WR 72.7%, Sharpe 0.43 (+19% vs TQQQ-010)
         Part B n=5, WR 60%, Sharpe 0.13 (-87% vs TQQQ-010)
    min(A,B) = 0.13（失敗，遠低於 TQQQ-010 的 0.36）
    失敗分析：
      - Part A 小幅改善因篩除部分 Part A 停損（2020-03-12、2021-09-28、
        2022-03-08、2022-09-21 四筆中篩除三筆）
      - 但 Part B 崩壞——ClosePos>=0.30 篩掉 TQQQ-010 原 7 個 Part B 勝者中 5 個
        （2024-04-19、2024-07-24、2024-09-06、2025-02-27、2025-04-04 均
        ClosePos<0.30），同時冷卻期偏移引入新壞訊號（2025-03-04 SL、2025-04-07 SL）
      - 核心問題：TQQQ 3x 槓桿 + 5-6% 日波動使恐慌日多收於當日低點附近
        （多數 TQQQ-010 勝者的 ClosePos < 30%），日內反轉發生於隔日而非當日
      - 再度驗證 cross_asset_lesson #6（ClosePos 邊界 ≤ 2% vol）在 TQQQ 5-6% vol 失效

Att2 — 2 日加速跌幅 <= -10%（加速過濾，避開慢磨下跌）
    進場：20d DD <= -15% + RSI(5)<25 + Volume>1.5x SMA20 + Return2D<=-0.10
    預期：篩除「慢磨跌至 -15% DD」的訊號（如 2022-03-08 Ukraine 供應衝擊）、
         保留「急速 2 日崩盤至 -15% DD」的真恐慌（COVID 系列、yen carry、關稅）

目標（Targets）：
    - min(A,B) Sharpe > 0.36（TQQQ-010 基線）
    - Part A/B 累計報酬差 < 30%（TQQQ-010 為 14% 已達標）
    - Part A/B 年化訊號差 < 50%（TQQQ-010 為 4.0/yr vs 4.0/yr）
    - 必須保留成交模型（隔日開盤市價 + 0.1% 滑價 + 悲觀認定）
"""

from dataclasses import dataclass

from trading.experiments.tqqq_001_capitulation.config import TQQQConfig


@dataclass
class TQQQ017Config(TQQQConfig):
    """TQQQ-017：恐慌抄底 + 加速/確認過濾配置

    繼承 TQQQ-001 的三重進場條件，依迭代選擇加入不同過濾器。
    出場參數沿用 TQQQ-008/010 的優化值（TP +7% / SL -8% / 10 天持倉）。
    """

    # 沿用 TQQQ-001 核心參數（繼承預設）：
    #   drawdown_lookback: 20, drawdown_threshold: -0.15
    #   rsi_period: 5, rsi_threshold: 25.0
    #   volume_multiplier: 1.5, volume_sma_period: 20
    #   cooldown_days: 3

    # Att1（ClosePos 日內反轉，已驗證失敗）
    # close_position_threshold 保留為可選參數，<=0 表示停用該過濾器
    close_position_threshold: float = 0.0  # 0.0 = 停用

    # Att2：2 日加速跌幅過濾
    two_day_return_threshold: float = -0.10  # 2 日報酬 <= -10% 才視為急速恐慌
    enable_two_day_filter: bool = True

    # 後續迭代備用過濾器（Att2 停用）
    prev_rsi_threshold: float = 0.0

    # 優化出場（同 TQQQ-008/010）
    profit_target: float = 0.07
    stop_loss: float = -0.08
    holding_days: int = 10

    # 成交模型
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ017Config:
    return TQQQ017Config(
        name="tqqq_017_cap_reversal_confirm",
        experiment_id="TQQQ-017",
        display_name="TQQQ Capitulation + Acceleration Confirmation",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
    )
