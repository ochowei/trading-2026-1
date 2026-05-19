"""FXI–CNY Currency-Regime-Gated MR (FXI-017)"""

from trading.experiments import register
from trading.experiments.fxi_017_cny_regime_mr.strategy import (
    FXI017CnyRegimeMRStrategy,
)

register("fxi_017_cny_regime_mr")(FXI017CnyRegimeMRStrategy)
