"""EEM Vol-Adaptive RSI(2) Deep Decline (EEM-003)"""

from trading.experiments import register
from trading.experiments.eem_003_vol_adaptive_deep_decline.strategy import (
    EEM003Strategy,
)

register("eem_003_vol_adaptive_deep_decline")(EEM003Strategy)
