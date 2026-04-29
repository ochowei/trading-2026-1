"""SIVR Williams Vix Fix Capitulation MR (SIVR-016)"""

from trading.experiments import register
from trading.experiments.sivr_016_wvf_capitulation_mr.strategy import SIVR016Strategy

register("sivr_016_wvf_capitulation_mr")(SIVR016Strategy)
