"""COPX Volume-Confirmed Capitulation MR (COPX-018)"""

from trading.experiments import register
from trading.experiments.copx_018_volume_confirmed_mr.strategy import (
    COPX018VolumeConfirmedMRStrategy,
)

register("copx_018_volume_confirmed_mr")(COPX018VolumeConfirmedMRStrategy)
