"""TQQQ 優化出場 + 成交模型 (TQQQ Optimized Exit + Execution Model) — TQQQ-010"""

from trading.experiments import register
from trading.experiments.tqqq_cap_exec_optimized.strategy import TQQQCapExecOptimizedStrategy

register("tqqq_cap_exec_optimized")(TQQQCapExecOptimizedStrategy)
