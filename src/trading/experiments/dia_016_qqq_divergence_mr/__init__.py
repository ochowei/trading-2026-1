"""DIA-QQQ Cross-Asset Divergence CEILING Regime-Gated MR (DIA-016)"""

from trading.experiments import register
from trading.experiments.dia_016_qqq_divergence_mr.strategy import DIA016Strategy

register("dia_016_qqq_divergence_mr")(DIA016Strategy)
