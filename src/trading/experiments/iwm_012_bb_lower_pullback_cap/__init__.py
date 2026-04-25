"""IWM BB 下軌 + 回檔上限混合進場 (IWM-012)"""

from trading.experiments import register
from trading.experiments.iwm_012_bb_lower_pullback_cap.strategy import (
    IWM012Strategy,
)

register("iwm_012_bb_lower_pullback_cap")(IWM012Strategy)
