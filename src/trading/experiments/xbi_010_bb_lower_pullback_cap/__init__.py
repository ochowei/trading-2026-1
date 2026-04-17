"""XBI BB 下軌 + 回檔上限混合進場 (XBI-010)"""

from trading.experiments import register
from trading.experiments.xbi_010_bb_lower_pullback_cap.strategy import (
    XBI010Strategy,
)

register("xbi_010_bb_lower_pullback_cap")(XBI010Strategy)
