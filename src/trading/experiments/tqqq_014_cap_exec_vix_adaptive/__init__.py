"""TQQQ VIX 自適應出場 + 成交模型 (TQQQ VIX-Adaptive Exit + Execution Model) — TQQQ-014"""

from trading.experiments import register
from trading.experiments.tqqq_014_cap_exec_vix_adaptive.strategy import TQQQVixAdaptiveStrategy

register("tqqq_014_cap_exec_vix_adaptive")(TQQQVixAdaptiveStrategy)
