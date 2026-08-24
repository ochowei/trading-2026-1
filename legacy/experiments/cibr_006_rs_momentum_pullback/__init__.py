"""CIBR Cybersecurity Sector RS Momentum Pullback (CIBR-006)"""

from trading.experiments import register
from trading.experiments.cibr_006_rs_momentum_pullback.strategy import (
    CIBRRSMomentumStrategy,
)

register("cibr_006_rs_momentum_pullback")(CIBRRSMomentumStrategy)
