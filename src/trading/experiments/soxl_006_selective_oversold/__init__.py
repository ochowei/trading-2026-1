"""SOXL 精選超賣 + 延長持倉 + 成交模型 (SOXL Selective Oversold + Extended Holding) — SOXL-006"""

from trading.experiments import register
from trading.experiments.soxl_006_selective_oversold.strategy import (
    SOXLSelectiveOversoldStrategy,
)

register("soxl_006_selective_oversold")(SOXLSelectiveOversoldStrategy)
