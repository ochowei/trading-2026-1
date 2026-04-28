"""IWM Capitulation-Depth Filter MR (IWM-013)"""

from trading.experiments import register
from trading.experiments.iwm_013_capitulation_filter.strategy import (
    IWM013Strategy,
)

register("iwm_013_capitulation_filter")(IWM013Strategy)
