from trading.experiments import register
from trading.experiments.tqqq_cap_qqq_confirm.strategy import TQQQCapQqqConfirmStrategy

@register("tqqq_cap_qqq_confirm")
class _TQQQCapQqqConfirmStrategyRegistration(TQQQCapQqqConfirmStrategy):
    pass
