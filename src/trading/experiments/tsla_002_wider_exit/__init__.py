"""TSLA 寬出場均值回歸 (TSLA-002)"""

from trading.experiments import register
from trading.experiments.tsla_002_wider_exit.strategy import TSLAWiderExitStrategy

register("tsla_002_wider_exit")(TSLAWiderExitStrategy)
