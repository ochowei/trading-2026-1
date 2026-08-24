"""TSM Volume-Confirmed RS Momentum Pullback (TSM-012)"""

from trading.experiments import register
from trading.experiments.tsm_012_volume_confirmed_rs_pullback.strategy import (
    TSMVolumeConfirmedStrategy,
)

register("tsm_012_volume_confirmed_rs_pullback")(TSMVolumeConfirmedStrategy)
