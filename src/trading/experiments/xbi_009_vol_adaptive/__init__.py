"""XBI 波動率自適應回檔 + Williams %R + 反轉K線 (XBI-009)"""

from trading.experiments import register
from trading.experiments.xbi_009_vol_adaptive.strategy import (
    XBI009Strategy,
)

register("xbi_009_vol_adaptive")(XBI009Strategy)
