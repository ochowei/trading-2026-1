"""COPX RSI(2) Short-Term Mean Reversion (COPX-006)"""

from trading.experiments import register
from trading.experiments.copx_006_pairs_fcx.strategy import (
    COPXPairsFCXStrategy,
)

register("copx_006_pairs_fcx")(COPXPairsFCXStrategy)
