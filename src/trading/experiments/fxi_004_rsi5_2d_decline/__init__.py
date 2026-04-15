"""FXI RSI(5) + 2-Day Decline Mean Reversion (FXI-004)"""

from trading.experiments import register
from trading.experiments.fxi_004_rsi5_2d_decline.strategy import FXI004Strategy

register("fxi_004_rsi5_2d_decline")(FXI004Strategy)
