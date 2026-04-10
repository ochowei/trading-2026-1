"""COPX Copper Sector RS Momentum Pullback (COPX-008)"""

from trading.experiments import register
from trading.experiments.copx_008_rs_momentum.strategy import (
    COPX008Strategy,
)

register("copx_008_rs_momentum")(COPX008Strategy)
