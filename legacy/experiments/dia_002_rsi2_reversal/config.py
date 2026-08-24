"""
DIA-002: RSI(2) 極端超賣均值回歸
(DIA RSI(2) Extreme Oversold Mean Reversion)

基於 SPY-004 的 RSI(2) 訊號架構，移植至 DIA。
DIA 與 SPY 同為大型指數 ETF（日波動 ~1.0-1.3%），參數直接沿用 SPY-004。

Based on SPY-004 RSI(2) signal architecture, adapted for DIA.
DIA and SPY are both large-cap index ETFs with similar volatility (~1.0-1.3%).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIARsi2Config(ExperimentConfig):
    """DIA RSI(2) 極端超賣均值回歸參數"""

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


def create_default_config() -> DIARsi2Config:
    return DIARsi2Config(
        name="dia_002_rsi2_reversal",
        experiment_id="DIA-002",
        display_name="DIA RSI(2) Extreme Oversold Reversal",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.025,  # -2.5%（與 TP 對稱）
        holding_days=15,  # 15 天
    )
