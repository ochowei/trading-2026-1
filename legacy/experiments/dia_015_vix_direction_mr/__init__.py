"""DIA ^VIX Forward-Looking Implied-Vol DIRECTION Regime-Gated MR (DIA-015)"""

from trading.experiments import register
from trading.experiments.dia_015_vix_direction_mr.strategy import DIA015Strategy

register("dia_015_vix_direction_mr")(DIA015Strategy)
