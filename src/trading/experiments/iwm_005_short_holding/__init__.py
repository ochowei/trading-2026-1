"""IWM RSI(2) 短持倉優化 (IWM-005)"""

from trading.experiments import register
from trading.experiments.iwm_005_short_holding.strategy import (
    IWM005Strategy,
)

register("iwm_005_short_holding")(IWM005Strategy)
