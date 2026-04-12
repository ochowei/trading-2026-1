"""EEM 無 ClosePos + ATR RSI(2) 均值回歸 (EEM-011)"""

from trading.experiments import register
from trading.experiments.eem_011_no_closepos_atr.strategy import EEM011Strategy

register("eem_011_no_closepos_atr")(EEM011Strategy)
