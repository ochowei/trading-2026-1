"""INDA DXY Direction Filter MR (INDA-012)"""

from trading.experiments import register
from trading.experiments.inda_012_dxy_direction_mr.strategy import (
    INDA012Strategy,
)

register("inda_012_dxy_direction_mr")(INDA012Strategy)
