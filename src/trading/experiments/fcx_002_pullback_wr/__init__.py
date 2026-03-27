"""FCX Pullback + Williams %R + Reversal Candle Mean Reversion (FCX-002)"""

from trading.experiments import register
from trading.experiments.fcx_002_pullback_wr.strategy import FCXPullbackWRStrategy

register("fcx_002_pullback_wr")(FCXPullbackWRStrategy)
