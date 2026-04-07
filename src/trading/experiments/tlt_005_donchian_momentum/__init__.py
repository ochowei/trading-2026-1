"""TLT Donchian 突破 + 趨勢跟蹤 (TLT-005)"""

from trading.experiments import register
from trading.experiments.tlt_005_donchian_momentum.strategy import (
    TLTBreakoutTrendStrategy,
)

register("tlt_005_donchian_momentum")(TLTBreakoutTrendStrategy)
