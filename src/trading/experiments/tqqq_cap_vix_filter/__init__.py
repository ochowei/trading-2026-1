"""TQQQ VIX 過濾實驗 (TQQQ VIX Filter Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_cap_vix_filter.strategy import TQQQCapVixFilterStrategy

register("tqqq_cap_vix_filter")(TQQQCapVixFilterStrategy)
