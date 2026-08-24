"""XBI 回檔 + Williams %R + 反轉K線 (XBI-005)"""

from trading.experiments import register
from trading.experiments.xbi_005_closepos_reversal.strategy import (
    XBI005Strategy,
)

register("xbi_005_closepos_reversal")(XBI005Strategy)
