"""TQQQ 基線恐慌抄底 + 成交模型 (TQQQ Baseline Capitulation + Execution Model) — TQQQ-011"""

from trading.experiments import register
from trading.experiments.tqqq_011_cap_exec_baseline.strategy import TQQQCapExecBaselineStrategy

register("tqqq_011_cap_exec_baseline")(TQQQCapExecBaselineStrategy)
