"""SOXL 寬停損均值回歸 + 成交模型 (SOXL Wide SL + Execution Model) — SOXL-003"""

from trading.experiments import register
from trading.experiments.soxl_003_wide_sl.strategy import SOXLWideSLStrategy

register("soxl_003_wide_sl")(SOXLWideSLStrategy)
