"""SIVR Donchian 通道突破策略 (SIVR-014)"""

from trading.experiments import register
from trading.experiments.sivr_014_donchian_breakout.strategy import (
    SIVRDonchianBreakoutStrategy,
)

register("sivr_014_donchian_breakout")(SIVRDonchianBreakoutStrategy)
