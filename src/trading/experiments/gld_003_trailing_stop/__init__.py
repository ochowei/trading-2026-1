"""GLD 追蹤停損均值回歸 (GLD-003)"""

from trading.experiments import register
from trading.experiments.gld_003_trailing_stop.strategy import GLDTrailingStopStrategy

register("gld_003_trailing_stop")(GLDTrailingStopStrategy)
