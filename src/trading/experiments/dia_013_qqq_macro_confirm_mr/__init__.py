"""DIA QQQ Macro-Confirmation Gate MR (DIA-013)"""

from trading.experiments import register
from trading.experiments.dia_013_qqq_macro_confirm_mr.strategy import DIA013Strategy

register("dia_013_qqq_macro_confirm_mr")(DIA013Strategy)
