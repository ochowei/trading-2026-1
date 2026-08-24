"""SPY 回檔 + WR + VIX 恐慌過濾（SPY-003）"""

from trading.experiments import register
from trading.experiments.spy_003_optimized_wr.strategy import (
    SPYVixFilterStrategy,
)

register("spy_003_optimized_wr")(SPYVixFilterStrategy)
