"""SOXL 優化出場 + 成交模型 (SOXL Optimized Exit + Execution Model) — SOXL-006"""

from trading.experiments import register
from trading.experiments.soxl_006_optimized_exit.strategy import SOXL006Strategy

register("soxl_006_optimized_exit")(SOXL006Strategy)
