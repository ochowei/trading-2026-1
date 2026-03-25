"""TQQQ 放寬進場實驗 (TQQQ Relaxed Entry Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_cap_relaxed_entry.strategy import TQQQCapRelaxedStrategy

register("tqqq_cap_relaxed_entry")(TQQQCapRelaxedStrategy)
