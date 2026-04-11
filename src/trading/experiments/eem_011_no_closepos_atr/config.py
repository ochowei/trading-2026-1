"""
EEM-011: 無 ClosePos + ATR 波動率自適應 RSI(2)
(EEM No ClosePos + ATR Volatility-Adaptive RSI(2))

測試移除 ClosePos 過濾器的效果：
- ClosePos 不可跨資產通用（lesson #34：GLD/IWM 有效但 USO/SIVR/FCX 無效）
- 保留 ATR(5)/ATR(20) > 1.1 和 2 日跌幅 >= 2.0% 作為主要品質過濾
- 驗證 ClosePos 對 EEM 是否有效
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM011Config(ExperimentConfig):
    """EEM-011 無 ClosePos + ATR 自適應 RSI(2) 參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.020

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.1

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> EEM011Config:
    return EEM011Config(
        name="eem_011_no_closepos_atr",
        experiment_id="EEM-011",
        display_name="EEM No ClosePos + ATR RSI(2)",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=20,
    )
