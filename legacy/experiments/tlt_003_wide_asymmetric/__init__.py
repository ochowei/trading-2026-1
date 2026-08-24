"""TLT 寬停損非對稱出場均值回歸 (TLT-003)"""

from trading.experiments import register
from trading.experiments.tlt_003_wide_asymmetric.strategy import (
    TLTWideAsymmetricStrategy,
)

register("tlt_003_wide_asymmetric")(TLTWideAsymmetricStrategy)
