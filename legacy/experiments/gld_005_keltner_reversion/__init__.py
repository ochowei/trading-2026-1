"""GLD Keltner 通道均值回歸 (GLD-005)"""

from trading.experiments import register
from trading.experiments.gld_005_keltner_reversion.strategy import (
    GLDKeltnerReversionStrategy,
)

register("gld_005_keltner_reversion")(GLDKeltnerReversionStrategy)
