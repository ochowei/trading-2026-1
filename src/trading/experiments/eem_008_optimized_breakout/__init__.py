"""EEM Optimized Breakout (EEM-008)"""

from trading.experiments import register
from trading.experiments.eem_008_optimized_breakout.strategy import EEM008Strategy

register("eem_008_optimized_breakout")(EEM008Strategy)
