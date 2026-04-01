"""XBI 回檔範圍收窄 + 長冷卻 均值回歸 (XBI-004)"""

from trading.experiments import register
from trading.experiments.xbi_004_capped_cooldown.strategy import (
    XBICappedCooldownStrategy,
)

register("xbi_004_capped_cooldown")(XBICappedCooldownStrategy)
