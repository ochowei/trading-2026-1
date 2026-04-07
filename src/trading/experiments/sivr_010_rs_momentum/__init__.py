"""SIVR Silver/Gold RS Momentum (SIVR-010)"""

from trading.experiments import register
from trading.experiments.sivr_010_rs_momentum.strategy import SIVRRSMomentumStrategy

register("sivr_010_rs_momentum")(SIVRRSMomentumStrategy)
