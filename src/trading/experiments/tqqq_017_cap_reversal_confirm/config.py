"""
TQQQ-017：恐慌抄底 + 日內反轉確認 (Capitulation + Intraday Recovery Confirmation)

動機（Motivation）：
    TQQQ-010（當前最佳）在 Part A 出現 6 筆停損（20 訊號中，WR 70%，
    Sharpe 0.36），拖累 min(A,B) 從 Part B 的 1.02 降至 0.36。
    Part A 停損日期：2020-02-24、2020-03-12、2021-09-28、2022-03-08、
    2022-09-01、2022-09-21。觀察這些日子的共同特徵與勝利日的差異，設計
    篩選器以過濾「持續性下跌中的偽訊號」但保留「急速恐慌後的真反轉」。

策略方向：均值回歸（加入日內反轉確認）

Att1 — ClosePos >= 0.30（日內反轉確認）
    進場：20d DD <= -15% + RSI(5)<25 + Volume>1.5x SMA20 + ClosePos>=0.30
    預期：ClosePos = (Close-Low)/(High-Low) >= 0.30 要求訊號日盤中收在當日振幅
         上段，確認已出現盤中反彈，排除「盤中持續性賣壓」的偽訊號。

與 cross_asset_lesson #6（ClosePos 邊界約為日波動 ≤ 2.0%）的關係：
    Lesson #6 基於 ClosePos 作為「日常訊號」過濾器的跨資產測試。本實驗情境不同：
    TQQQ-010 訊號已要求三重極端條件（DD ≤ -15% + RSI(5)<25 + Volume > 1.5x SMA20），
    ClosePos 僅作為**恐慌日日內反轉確認**而非獨立訊號。此 context 下 ClosePos 在
    高波動資產是否有效為 open question，本實驗直接驗證。

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
    """TQQQ-017：恐慌抄底 + 日內反轉確認配置

    繼承 TQQQ-001 的三重進場條件，加入 close_position_threshold。
    出場參數沿用 TQQQ-008/010 的優化值（TP +7% / SL -8% / 10 天持倉）。
    """

    # 沿用 TQQQ-001 核心參數（繼承預設）：
    #   drawdown_lookback: 20, drawdown_threshold: -0.15
    #   rsi_period: 5, rsi_threshold: 25.0
    #   volume_multiplier: 1.5, volume_sma_period: 20
    #   cooldown_days: 3

    # Att1：日內反轉確認
    close_position_threshold: float = 0.30  # ClosePos = (Close-Low)/(High-Low) >= 0.30

    # 後續迭代備用過濾器（Att1 停用）
    two_day_return_threshold: float = -0.10
    enable_two_day_filter: bool = False
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
        display_name="TQQQ Capitulation + Intraday Recovery Confirmation",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
    )
