"""TSM Earnings-Date Exclusion Filter on RS Momentum Pullback (TSM-017)"""

from trading.experiments import register
from trading.experiments.tsm_017_earnings_exclusion.strategy import (
    TSMEarningsExclusionStrategy,
)

register("tsm_017_earnings_exclusion")(TSMEarningsExclusionStrategy)
