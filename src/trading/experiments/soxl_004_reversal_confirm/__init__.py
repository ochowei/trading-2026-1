"""SOXL 反轉確認均值回歸 + 成交模型 (SOXL Reversal Confirm + Execution Model) — SOXL-004"""

from trading.experiments import register
from trading.experiments.soxl_004_reversal_confirm.strategy import (
    SOXLReversalConfirmStrategy,
)

register("soxl_004_reversal_confirm")(SOXLReversalConfirmStrategy)
