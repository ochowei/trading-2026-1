from trading.experiments import register
from trading.experiments.tqqq_momentum_collapse.strategy import TQQQMomentumCollapseStrategy

@register("tqqq_momentum_collapse")
class _TQQQMomentumCollapseStrategyRegistration(TQQQMomentumCollapseStrategy):
    pass
