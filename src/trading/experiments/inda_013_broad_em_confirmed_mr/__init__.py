"""INDA Broad-EM Macro-Context-Confirmed Vol-Transition MR (INDA-013)"""

from trading.experiments import register
from trading.experiments.inda_013_broad_em_confirmed_mr.strategy import INDA013Strategy

register("inda_013_broad_em_confirmed_mr")(INDA013Strategy)
