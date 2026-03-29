"""
TSM SMH Semiconductor Confirmation Experiment
"""

from trading.experiments import register
from trading.experiments.tsm_004_smh_confirm.strategy import (
    TSMSMHConfirmStrategy,
)

register("tsm_004_smh_confirm")(TSMSMHConfirmStrategy)
