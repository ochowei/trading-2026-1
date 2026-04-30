"""SIVR Money Flow Index Capitulation Mean Reversion (SIVR-017)"""

from trading.experiments import register
from trading.experiments.sivr_017_mfi_capitulation_mr.strategy import (
    SIVRMFICapitulationMRStrategy,
)

register("sivr_017_mfi_capitulation_mr")(SIVRMFICapitulationMRStrategy)
