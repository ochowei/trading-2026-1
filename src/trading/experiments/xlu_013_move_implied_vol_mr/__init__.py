"""XLU MOVE Implied-Vol Forward-Looking Regime-Gated MR (XLU-013)"""

from trading.experiments import register
from trading.experiments.xlu_013_move_implied_vol_mr.strategy import (
    XLU013Strategy,
)

register("xlu_013_move_implied_vol_mr")(XLU013Strategy)
