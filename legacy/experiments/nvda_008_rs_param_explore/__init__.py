"""NVDA RS Parameter Exploration (NVDA-008)"""

from trading.experiments import register
from trading.experiments.nvda_008_rs_param_explore.strategy import (
    NVDARSParamExploreStrategy,
)

register("nvda_008_rs_param_explore")(NVDARSParamExploreStrategy)
