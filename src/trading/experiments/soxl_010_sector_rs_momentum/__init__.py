"""SOXL Semiconductor Sector RS Momentum Pullback (SOXL-010)"""

from trading.experiments import register
from trading.experiments.soxl_010_sector_rs_momentum.strategy import (
    SOXLSectorRSStrategy,
)

register("soxl_010_sector_rs_momentum")(SOXLSectorRSStrategy)
