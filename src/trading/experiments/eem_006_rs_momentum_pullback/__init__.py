"""EEM RS Momentum Pullback (EEM-006)"""

from trading.experiments import register
from trading.experiments.eem_006_rs_momentum_pullback.strategy import (
    EEMRSMomentumStrategy,
)

register("eem_006_rs_momentum_pullback")(EEMRSMomentumStrategy)
