"""TQQQ QQQ 確認 + 成交模型 (TQQQ QQQ Confirmation + Execution Model) — TQQQ-012"""

from trading.experiments import register
from trading.experiments.tqqq_cap_exec_qqq_confirm.strategy import TQQQCapExecQqqConfirmStrategy

register("tqqq_cap_exec_qqq_confirm")(TQQQCapExecQqqConfirmStrategy)
