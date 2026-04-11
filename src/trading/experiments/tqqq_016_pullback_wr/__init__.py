"""TQQQ 回檔 + Williams %R 均值回歸 (TQQQ-016)"""

from trading.experiments import register
from trading.experiments.tqqq_016_pullback_wr.strategy import (
    TQQQPullbackWRStrategy,
)

register("tqqq_016_pullback_wr")(TQQQPullbackWRStrategy)
