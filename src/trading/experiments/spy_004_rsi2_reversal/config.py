"""
SPY-004: RSI(2) 極端超賣均值回歸
(SPY RSI(2) Extreme Oversold Mean Reversion)

完全不同的訊號架構：使用 RSI(2) 捕捉極端 2 日動量耗竭，
搭配 2 日累計跌幅過濾與收盤位置反轉確認。

相較 SPY-002 的 10 日高點回檔架構，RSI(2) 更短期且更不受
市場週期影響，預期改善 Part A/B 訊號平衡。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYRsi2Config(ExperimentConfig):
    """SPY RSI(2) 極端超賣均值回歸參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10（極端超賣）

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) >= 40%

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> SPYRsi2Config:
    return SPYRsi2Config(
        name="spy_004_rsi2_reversal",
        experiment_id="SPY-004",
        display_name="SPY RSI(2) Extreme Oversold Reversal",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.025,  # -2.5%（與 TP 對稱）
        holding_days=15,  # 15 天
    )
