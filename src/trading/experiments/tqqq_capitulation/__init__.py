"""TQQQ 恐慌抄底實驗 (TQQQ Capitulation Buy Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_capitulation.strategy import TQQQStrategy

register("tqqq_capitulation")(TQQQStrategy)
