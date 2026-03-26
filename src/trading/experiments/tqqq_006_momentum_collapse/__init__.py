"""TQQQ 多日動能崩潰實驗 (TQQQ Multi-Day Momentum Collapse Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_006_momentum_collapse.strategy import TQQQMomentumCollapseStrategy

register("tqqq_006_momentum_collapse")(TQQQMomentumCollapseStrategy)
