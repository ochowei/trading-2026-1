"""
XBI-009: RSI(2) 均值回歸 + 反轉K線
(XBI RSI(2) Mean Reversion + Reversal Candlestick)

Att1: ATR(5)/ATR(20) > 1.1 + XBI-005 框架 → Part A 0.27/Part B 0.16，太嚴移除好訊號
Att2: ATR > 1.05 → Part A -0.08/Part B 0.36，新增訊號反而是壞訊號
  → ATR 過濾在 XBI 2.0% 日波動確認失效（與 SIVR 2-3% 失敗一致）
Att3: 改用 RSI(2) 進場框架（SPY/DIA/IWM 最成功的均值回歸方法）
  RSI(2)<10 + 2日跌幅>=3.0% + ClosePos>=35%，TP+3.5%/SL-5.0%/15天
  參數按 XBI ~2.0% 日波動縮放（vs IWM 2.5% 跌幅，XBI 用 3.0%）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI009Config(ExperimentConfig):
    """XBI-009 RSI(2) 均值回歸參數"""

    # RSI(2) 進場（參考 IWM-005/SPY-005）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.030  # 2 日跌幅 >= 3.0%（XBI 波動略高於 IWM）

    # 反轉K線確認（XBI-005 驗證有效）
    close_position_threshold: float = 0.35  # ClosePos >= 35%

    cooldown_days: int = 10


def create_default_config() -> XBI009Config:
    return XBI009Config(
        name="xbi_009_vol_adaptive",
        experiment_id="XBI-009",
        display_name="XBI RSI(2) Mean Reversion + Reversal",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 XBI-005）
        stop_loss=-0.050,  # -5.0%（同 XBI-005）
        holding_days=15,  # 15 天（同 XBI-005）
    )
