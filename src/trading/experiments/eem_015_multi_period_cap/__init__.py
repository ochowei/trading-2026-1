"""EEM Multi-Period Capitulation-Strength Filter MR (EEM-015 Att1)"""

from trading.experiments import register
from trading.experiments.eem_015_multi_period_cap.strategy import (
    EEM015Strategy,
)

register("eem_015_multi_period_cap")(EEM015Strategy)
