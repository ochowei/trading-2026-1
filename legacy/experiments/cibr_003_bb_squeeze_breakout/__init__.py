"""CIBR BB 擠壓突破 (CIBR-003)"""

from trading.experiments import register
from trading.experiments.cibr_003_bb_squeeze_breakout.strategy import (
    CIBRBBSqueezeStrategy,
)

register("cibr_003_bb_squeeze_breakout")(CIBRBBSqueezeStrategy)
