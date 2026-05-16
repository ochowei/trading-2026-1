"""TQQQ QQQ Single-Day Momentum-Reversal MR → Trade TQQQ (TQQQ-027)"""

from trading.experiments import register
from trading.experiments.tqqq_027_qqq_single_day_reversal.strategy import (
    TQQQ027QqqReversalStrategy,
)

register("tqqq_027_qqq_single_day_reversal")(TQQQ027QqqReversalStrategy)
