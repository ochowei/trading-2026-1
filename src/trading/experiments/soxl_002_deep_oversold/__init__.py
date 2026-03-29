"""SOXL 深度超賣均值回歸 + 成交模型 (SOXL Deep Oversold + Execution Model) — SOXL-002"""

from trading.experiments import register
from trading.experiments.soxl_002_deep_oversold.strategy import SOXLDeepOversoldStrategy

register("soxl_002_deep_oversold")(SOXLDeepOversoldStrategy)
