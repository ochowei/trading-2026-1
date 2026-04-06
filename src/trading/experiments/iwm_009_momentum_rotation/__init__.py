"""IWM Small-Cap Rotation IWM/SPY (IWM-009)"""

from trading.experiments import register
from trading.experiments.iwm_009_momentum_rotation.strategy import (
    IWM009Strategy,
)

register("iwm_009_momentum_rotation")(IWM009Strategy)
