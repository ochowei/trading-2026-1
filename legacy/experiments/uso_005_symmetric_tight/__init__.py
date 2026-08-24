"""USO 對稱 TP/SL + 短持倉均值回歸 (USO-005)"""

from trading.experiments import register
from trading.experiments.uso_005_symmetric_tight.strategy import (
    USOSymmetricTightStrategy,
)

register("uso_005_symmetric_tight")(USOSymmetricTightStrategy)
