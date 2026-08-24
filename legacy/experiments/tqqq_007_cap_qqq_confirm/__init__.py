"""TQQQ QQQ 相對強度確認實驗 (TQQQ QQQ Confirmation Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_007_cap_qqq_confirm.strategy import TQQQCapQqqConfirmStrategy

register("tqqq_007_cap_qqq_confirm")(TQQQCapQqqConfirmStrategy)
