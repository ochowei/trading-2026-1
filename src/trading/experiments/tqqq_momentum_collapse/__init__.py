"""
TQQQ 多日動能崩潰策略 (TQQQ Multi-Day Momentum Collapse Strategy)
"""

from trading.experiments import register
from trading.experiments.tqqq_momentum_collapse.strategy import TQQQMomentumCollapseStrategy

register("tqqq_momentum_collapse")(TQQQMomentumCollapseStrategy)
