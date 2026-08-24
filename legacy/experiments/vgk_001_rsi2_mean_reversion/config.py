"""
VGK-001: RSI(2) 均值回歸
(VGK RSI(2) Mean Reversion)

基於 SPY-005 RSI(2) 寬出場架構，適用於 VGK（歐洲大盤 ETF）。
VGK 日波動 ~1.12%，與 SPY (~1.2%) 近似，使用相同參數架構：
- RSI(2) < 10 極端超賣
- 2 日跌幅 >= 1.5% 幅度確認
- ClosePos >= 40% 日內反轉確認
- TP +3.0% / SL -3.0% / 持倉 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGKRsi2MeanReversionConfig(ExperimentConfig):
    """VGK RSI(2) 均值回歸參數"""

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


def create_default_config() -> VGKRsi2MeanReversionConfig:
    return VGKRsi2MeanReversionConfig(
        name="vgk_001_rsi2_mean_reversion",
        experiment_id="VGK-001",
        display_name="VGK RSI(2) Mean Reversion",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
