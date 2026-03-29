"""SOXL 回撤範圍限制 + 成交模型 (SOXL Capped Drawdown + Execution Model) — SOXL-005"""

from trading.experiments import register
from trading.experiments.soxl_005_capped_drawdown.strategy import (
    SOXLCappedDrawdownStrategy,
)

register("soxl_005_capped_drawdown")(SOXLCappedDrawdownStrategy)
