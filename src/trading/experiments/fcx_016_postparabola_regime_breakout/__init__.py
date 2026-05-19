"""FCX Post-Parabolic Long-Horizon Regime Gate on VIX-FLOOR BB Squeeze Breakout (FCX-016)"""

from trading.experiments import register
from trading.experiments.fcx_016_postparabola_regime_breakout.strategy import (
    FCX016PostparabolaRegimeBreakoutStrategy,
)

register("fcx_016_postparabola_regime_breakout")(FCX016PostparabolaRegimeBreakoutStrategy)
