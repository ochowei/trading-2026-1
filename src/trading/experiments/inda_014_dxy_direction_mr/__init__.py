"""INDA DXY Direction Filter MR (INDA-014)"""

from trading.experiments import register
from trading.experiments.inda_014_dxy_direction_mr.strategy import (
    INDA014Strategy,
)

register("inda_014_dxy_direction_mr")(INDA014Strategy)
