"""URA 非對稱出場 + 回檔範圍收窄 (URA-002)"""

from trading.experiments import register
from trading.experiments.ura_002_asymmetric_narrow.strategy import (
    URAAsymmetricNarrowStrategy,
)

register("ura_002_asymmetric_narrow")(URAAsymmetricNarrowStrategy)
