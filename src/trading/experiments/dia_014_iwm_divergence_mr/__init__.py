"""DIA-IWM Cross-Asset Divergence CEILING Regime-Gated MR (DIA-014)"""

from trading.experiments import register
from trading.experiments.dia_014_iwm_divergence_mr.strategy import DIA014Strategy

register("dia_014_iwm_divergence_mr")(DIA014Strategy)
