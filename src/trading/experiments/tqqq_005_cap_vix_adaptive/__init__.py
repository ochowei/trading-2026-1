"""TQQQ 軟性 VIX + 適應性出場實驗 (TQQQ Soft VIX + Adaptive Exit Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_005_cap_vix_adaptive.strategy import TQQQCapVixAdaptiveStrategy

register("tqqq_005_cap_vix_adaptive")(TQQQCapVixAdaptiveStrategy)
