"""EEM ATR + 寬 SL RSI(2) 均值回歸 (EEM-009)"""

from trading.experiments import register
from trading.experiments.eem_009_atr_sl_rsi2.strategy import EEM009Strategy

register("eem_009_atr_sl_rsi2")(EEM009Strategy)
