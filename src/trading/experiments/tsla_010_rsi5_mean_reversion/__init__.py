"""TSLA RSI(5) Mean Reversion (SOXL-006 Framework) — TSLA-010"""

from trading.experiments import register
from trading.experiments.tsla_010_rsi5_mean_reversion.strategy import (
    TSLARSI5MeanRevStrategy,
)

register("tsla_010_rsi5_mean_reversion")(TSLARSI5MeanRevStrategy)
