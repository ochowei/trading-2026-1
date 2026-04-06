"""XLU RSI(2) Wide Stop-Loss Mean Reversion (XLU-006)"""

from trading.experiments import register
from trading.experiments.xlu_006_rsi2_wide_sl.strategy import XLURSI2WideSLStrategy

register("xlu_006_rsi2_wide_sl")(XLURSI2WideSLStrategy)
