"""FXI Stochastic %K/%D Crossover MR (FXI-008)"""

from trading.experiments import register
from trading.experiments.fxi_008_stochastic_mr.strategy import FXI008Strategy

register("fxi_008_stochastic_mr")(FXI008Strategy)
