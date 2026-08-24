"""TSLA 緊密回撤範圍均值回歸 (TSLA-003)"""

from trading.experiments import register
from trading.experiments.tsla_003_tight_retracement.strategy import (
    TSLATightRetracementStrategy,
)

register("tsla_003_tight_retracement")(TSLATightRetracementStrategy)
