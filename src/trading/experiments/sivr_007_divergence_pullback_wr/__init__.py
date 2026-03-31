"""SIVR 回檔範圍 + Williams %R + RSI 動能回復 均值回歸 (SIVR-007)"""

from trading.experiments import register
from trading.experiments.sivr_007_divergence_pullback_wr.strategy import (
    SIVRDivergencePullbackWRStrategy,
)

register("sivr_007_divergence_pullback_wr")(SIVRDivergencePullbackWRStrategy)
