"""
EEM-001: RSI(2) 均值回歸
(EEM RSI(2) Mean Reversion)

基於 SPY-005 RSI(2) 寬出場架構，適用於 EEM（新興市場 ETF）。
EEM 日波動 ~1.17%，與 SPY (~1.2%) 近似，使用相同參數架構：
- RSI(2) < 10 極端超賣
- 2 日跌幅 >= 1.5% 幅度確認
- ClosePos >= 40% 日內反轉確認
- TP +3.0% / SL -3.0% / 持倉 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEMRsi2MeanReversionConfig(ExperimentConfig):
    """EEM RSI(2) 均值回歸參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> EEMRsi2MeanReversionConfig:
    return EEMRsi2MeanReversionConfig(
        name="eem_001_rsi2_mean_reversion",
        experiment_id="EEM-001",
        display_name="EEM RSI(2) Mean Reversion",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
