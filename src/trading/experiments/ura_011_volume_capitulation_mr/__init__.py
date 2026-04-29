"""URA Volume-Confirmed Capitulation Mean Reversion (URA-011)"""

from trading.experiments import register
from trading.experiments.ura_011_volume_capitulation_mr.strategy import URA011Strategy

register("ura_011_volume_capitulation_mr")(URA011Strategy)
