"""TQQQ QQQ 確認 + 優化出場 + 成交模型 (TQQQ-013)"""

from trading.experiments import register
from trading.experiments.tqqq_013_cap_exec_qqq_optimized.strategy import TQQQCapExecQqqOptimizedStrategy

register("tqqq_013_cap_exec_qqq_optimized")(TQQQCapExecQqqOptimizedStrategy)
