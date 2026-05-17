"""FXI–CNY Currency-Regime-Gated MR (FXI-015)"""

from trading.experiments import register
from trading.experiments.fxi_015_cny_regime_mr.strategy import (
    FXI015CnyRegimeMRStrategy,
)

register("fxi_015_cny_regime_mr")(FXI015CnyRegimeMRStrategy)
