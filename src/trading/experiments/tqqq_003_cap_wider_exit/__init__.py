"""TQQQ 加寬出場實驗 (TQQQ Wider Exit Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_003_cap_wider_exit.strategy import TQQQCapWiderExitStrategy

register("tqqq_003_cap_wider_exit")(TQQQCapWiderExitStrategy)
