"""TSLA DXY 5d Direction Filter on TSLA-QQQ Cross-Asset Divergence BB Squeeze Breakout (TSLA-018)"""

from trading.experiments import register
from trading.experiments.tsla_018_dxy_direction_breakout.strategy import (
    TSLA018DXYDirectionBreakoutStrategy,
)

register("tsla_018_dxy_direction_breakout")(TSLA018DXYDirectionBreakoutStrategy)
