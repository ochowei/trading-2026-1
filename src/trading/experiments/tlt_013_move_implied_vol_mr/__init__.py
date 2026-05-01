"""TLT MOVE Implied Volatility Forward-Looking Regime-Gated MR (TLT-013)"""

from trading.experiments import register
from trading.experiments.tlt_013_move_implied_vol_mr.strategy import (
    TLT013MoveImpliedVolMRStrategy,
)

register("tlt_013_move_implied_vol_mr")(TLT013MoveImpliedVolMRStrategy)
