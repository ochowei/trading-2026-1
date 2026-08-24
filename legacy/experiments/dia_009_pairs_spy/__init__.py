"""DIA Pairs Trading DIA/SPY (DIA-009)"""

from trading.experiments import register
from trading.experiments.dia_009_pairs_spy.strategy import (
    DIAPairsSPYStrategy,
)

register("dia_009_pairs_spy")(DIAPairsSPYStrategy)
