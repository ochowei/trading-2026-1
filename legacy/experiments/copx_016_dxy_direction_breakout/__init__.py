"""COPX-016: DXY Direction Filter on Regime-Aware BB Squeeze Breakout"""

from trading.experiments import register
from trading.experiments.copx_016_dxy_direction_breakout.strategy import (
    COPX016DXYDirectionStrategy,
)

register("copx_016_dxy_direction_breakout")(COPX016DXYDirectionStrategy)
