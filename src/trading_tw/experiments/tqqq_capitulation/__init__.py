"""TQQQ 恐慌抄底實驗 (TQQQ Capitulation Buy Experiment)"""

from trading_tw.experiments import register
from trading_tw.experiments.tqqq_capitulation.strategy import TQQQStrategy

register("tqqq_capitulation")(TQQQStrategy)
