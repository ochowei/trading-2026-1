"""
IBIT-003: RSI(5) Trend Pullback 配置
IBIT RSI(5) Trend Pullback Configuration

Att1（BB 擠壓突破）失敗：Part A -0.29 / Part B -1.11
Att2（趨勢動量回檔）失敗：Part A -0.07 / Part B 僅 1 訊號

Attempt 3 假說：使用 RSI(5)（SOXL 驗證有效的高波動振盪器）搭配較寬鬆的
SMA(20) 趨勢確認，以在 IBIT 有限的 2 年數據中產生足夠的訊號。
TP +5% 匹配 IBIT-001 的已驗證 TP 上限。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBITRsi5TrendConfig(ExperimentConfig):
    """IBIT RSI(5) Trend Pullback 策略專屬參數"""

    sma_trend_period: int = 20
    rsi_period: int = 5
    rsi_threshold: float = 25.0  # RSI(5) < 25
    cooldown_days: int = 7


def create_default_config() -> IBITRsi5TrendConfig:
    """建立預設配置"""
    return IBITRsi5TrendConfig(
        name="ibit_003_bb_squeeze_breakout",
        experiment_id="IBIT-003",
        display_name="IBIT RSI(5) Trend Pullback",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,  # +5.0%
        stop_loss=-0.07,  # -7.0%
        holding_days=15,
    )
