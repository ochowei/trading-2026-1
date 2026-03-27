"""SOXL 極端超賣均值回歸 + 成交模型 (SOXL Extreme Oversold + Execution Model) — SOXL-001"""

from trading.experiments import register
from trading.experiments.soxl_001_extreme_oversold.strategy import SOXLExtremeOversoldStrategy

register("soxl_001_extreme_oversold")(SOXLExtremeOversoldStrategy)
