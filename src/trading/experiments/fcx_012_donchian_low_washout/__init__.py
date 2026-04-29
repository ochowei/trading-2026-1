"""FCX Donchian Lower Washout + Intraday Reversal MR (FCX-012)"""

from trading.experiments import register
from trading.experiments.fcx_012_donchian_low_washout.strategy import FCX012Strategy

register("fcx_012_donchian_low_washout")(FCX012Strategy)
