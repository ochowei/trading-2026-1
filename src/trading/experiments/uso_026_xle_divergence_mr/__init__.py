"""USO-XLE Cross-Asset Divergence Regime-Gated MR (USO-026)"""

from trading.experiments import register
from trading.experiments.uso_026_xle_divergence_mr.strategy import USO026Strategy

register("uso_026_xle_divergence_mr")(USO026Strategy)
