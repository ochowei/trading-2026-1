"""TSLA Williams %R 均值回歸 (TSLA-004)"""

from trading.experiments import register
from trading.experiments.tsla_004_wr_reversion.strategy import TSLAWRReversionStrategy

register("tsla_004_wr_reversion")(TSLAWRReversionStrategy)
