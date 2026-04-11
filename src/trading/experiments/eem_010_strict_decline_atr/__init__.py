"""EEM 嚴格跌幅 + ATR RSI(2) 均值回歸 (EEM-010)"""

from trading.experiments import register
from trading.experiments.eem_010_strict_decline_atr.strategy import EEM010Strategy

register("eem_010_strict_decline_atr")(EEM010Strategy)
