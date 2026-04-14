"""EWT RSI(2) Volatility-Adaptive Mean Reversion (EWT-005)"""

from trading.experiments import register
from trading.experiments.ewt_005_rsi2_vol_adaptive.strategy import EWT005Strategy

register("ewt_005_rsi2_vol_adaptive")(EWT005Strategy)
