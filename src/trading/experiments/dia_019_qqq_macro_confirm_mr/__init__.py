"""DIA QQQ Macro-Confirmation Gate MR (DIA-019)"""

from trading.experiments import register
from trading.experiments.dia_019_qqq_macro_confirm_mr.strategy import DIA019Strategy

register("dia_019_qqq_macro_confirm_mr")(DIA019Strategy)
