"""TLT ^MOVE Multi-Window IV Direction Regime-Gated MR (TLT-016)"""

from trading.experiments import register
from trading.experiments.tlt_016_move_multi_window_direction_mr.strategy import (
    TLT016MoveMultiWindowDirectionMRStrategy,
)

register("tlt_016_move_multi_window_direction_mr")(TLT016MoveMultiWindowDirectionMRStrategy)
