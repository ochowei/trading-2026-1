"""SPY Signal-Day Capitulation-Strength Filter MR (SPY-009)"""

from trading.experiments import register
from trading.experiments.spy_009_capitulation_filter.strategy import SPY009Strategy

register("spy_009_capitulation_filter")(SPY009Strategy)
