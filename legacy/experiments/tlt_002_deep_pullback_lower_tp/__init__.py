"""TLT 深度回檔 + 較低獲利目標 均值回歸 (TLT-002)"""

from trading.experiments import register
from trading.experiments.tlt_002_deep_pullback_lower_tp.strategy import (
    TLTDeepPullbackLowerTPStrategy,
)

register("tlt_002_deep_pullback_lower_tp")(TLTDeepPullbackLowerTPStrategy)
