"""URA Post-Parabolic Long-Horizon Regime-Gated Capitulation MR (URA-014)"""

from trading.experiments import register
from trading.experiments.ura_014_postparabola_regime_mr.strategy import URA014Strategy

register("ura_014_postparabola_regime_mr")(URA014Strategy)
