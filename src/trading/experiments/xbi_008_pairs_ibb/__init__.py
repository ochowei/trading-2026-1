"""XBI-008: XBI/IBB Pairs Trading"""

from trading.experiments import register
from trading.experiments.xbi_008_pairs_ibb.strategy import XBIPairsIBBStrategy

register("xbi_008_pairs_ibb")(XBIPairsIBBStrategy)
