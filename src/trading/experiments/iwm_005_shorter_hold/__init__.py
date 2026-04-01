"""IWM RSI(2) Shorter Hold (IWM-005)"""

from trading.experiments import register
from trading.experiments.iwm_005_shorter_hold.strategy import (
    IWM005Strategy,
)

register("iwm_005_shorter_hold")(IWM005Strategy)
