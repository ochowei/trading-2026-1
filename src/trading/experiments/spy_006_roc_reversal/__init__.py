"""SPY ROC 速度衰減均值回歸 (SPY-006)"""

from trading.experiments import register
from trading.experiments.spy_006_roc_reversal.strategy import (
    SPYROCReversalStrategy,
)

register("spy_006_roc_reversal")(SPYROCReversalStrategy)
