"""URA 趨勢回調買入 (URA-006)"""

from trading.experiments import register
from trading.experiments.ura_006_trend_pullback.strategy import (
    URATrendPullbackStrategy,
)

register("ura_006_trend_pullback")(URATrendPullbackStrategy)
