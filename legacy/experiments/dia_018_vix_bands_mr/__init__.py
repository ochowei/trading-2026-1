"""DIA ^VIX Implied-Vol BANDS (U-shape Regime) Gated MR (DIA-018)"""

from trading.experiments import register
from trading.experiments.dia_018_vix_bands_mr.strategy import DIA018Strategy

register("dia_018_vix_bands_mr")(DIA018Strategy)
