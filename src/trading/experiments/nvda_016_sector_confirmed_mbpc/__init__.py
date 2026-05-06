"""NVDA Sector-Health Confirmed Multi-Week Regime-Aware MBPC (NVDA-016)"""

from trading.experiments import register
from trading.experiments.nvda_016_sector_confirmed_mbpc.strategy import (
    NVDA016SectorConfirmedMBPCStrategy,
)

register("nvda_016_sector_confirmed_mbpc")(NVDA016SectorConfirmedMBPCStrategy)
