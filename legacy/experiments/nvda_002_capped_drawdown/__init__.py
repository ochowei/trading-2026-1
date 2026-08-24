"""
NVDA Capped Drawdown Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.nvda_002_capped_drawdown.strategy import NVDACappedDrawdownStrategy

register("nvda_002_capped_drawdown")(NVDACappedDrawdownStrategy)
