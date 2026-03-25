from trading.experiments import register
from trading.experiments.tqqq_cap_vix_adaptive.strategy import TQQQCapVixAdaptiveStrategy

@register("tqqq_cap_vix_adaptive")
class _TQQQCapVixAdaptiveStrategyRegistration(TQQQCapVixAdaptiveStrategy):
    pass
