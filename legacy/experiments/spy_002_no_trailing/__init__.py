"""SPY 回檔 + WR + 反轉K線（無追蹤停損）(SPY-002)"""

from trading.experiments import register
from trading.experiments.spy_002_no_trailing.strategy import (
    SPYNoTrailingStrategy,
)

register("spy_002_no_trailing")(SPYNoTrailingStrategy)
