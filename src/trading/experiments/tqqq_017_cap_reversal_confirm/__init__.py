"""TQQQ 恐慌抄底 + 日內反轉確認 (TQQQ-017)"""

from trading.experiments import register
from trading.experiments.tqqq_017_cap_reversal_confirm.strategy import (
    TQQQ017Strategy,
)

register("tqqq_017_cap_reversal_confirm")(TQQQ017Strategy)
