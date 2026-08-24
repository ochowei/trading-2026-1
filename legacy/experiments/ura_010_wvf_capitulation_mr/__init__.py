"""URA Williams Vix Fix Capitulation Mean Reversion (URA-010)"""

from trading.experiments import register
from trading.experiments.ura_010_wvf_capitulation_mr.strategy import (
    URA010WVFCapitulationStrategy,
)

register("ura_010_wvf_capitulation_mr")(URA010WVFCapitulationStrategy)
