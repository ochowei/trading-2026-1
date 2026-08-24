"""
IWM-003: RSI(2) 極端超賣均值回歸（出場優化）
(IWM RSI(2) Extreme Oversold Mean Reversion - Optimized Exit)

延續 IWM-001 的 RSI(2) 進場架構，測試出場參數優化：
- TP +3.5%（IWM-002 用 pullback 框架測試過 +3.5% 但非 RSI(2) 框架）
- SL -4.5%（已驗證最佳值）
- 持倉 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWMRsi2OptConfig(ExperimentConfig):
    """IWM RSI(2) 極端超賣均值回歸（出場優化）參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.025  # 2 日跌幅 >= 2.5%

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # >= 40%

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> IWMRsi2OptConfig:
    return IWMRsi2OptConfig(
        name="iwm_003_rsi2_optimized",
        experiment_id="IWM-003",
        display_name="IWM RSI(2) Optimized Exit",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（從 +3.0% 提高）
        stop_loss=-0.045,  # -4.5%（維持已驗證值）
        holding_days=20,  # 20 天
    )
