"""TSM BB-Width Regime Gate on RS Momentum Pullback (TSM-016)"""

from trading.experiments import register
from trading.experiments.tsm_016_bb_width_regime_gate.strategy import (
    TSMBBWidthRegimeGateStrategy,
)

register("tsm_016_bb_width_regime_gate")(TSMBBWidthRegimeGateStrategy)
