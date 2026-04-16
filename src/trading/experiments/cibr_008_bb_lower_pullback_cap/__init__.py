"""CIBR BB 下軌 + 回檔上限混合進場 (CIBR-008)"""

from trading.experiments import register
from trading.experiments.cibr_008_bb_lower_pullback_cap.strategy import (
    CIBR008Strategy,
)

register("cibr_008_bb_lower_pullback_cap")(CIBR008Strategy)
