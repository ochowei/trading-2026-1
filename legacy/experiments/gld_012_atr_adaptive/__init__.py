"""GLD 波動率自適應均值回歸 (GLD-012)"""

from trading.experiments import register
from trading.experiments.gld_012_atr_adaptive.strategy import GLD012Strategy

register("gld_012_atr_adaptive")(GLD012Strategy)
