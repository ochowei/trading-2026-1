"""USO 緊密回檔上限 + RSI(2) + 2日急跌均值回歸 (USO-013)"""

from trading.experiments import register
from trading.experiments.uso_013_tight_cap.strategy import (
    USOTightCapStrategy,
)

register("uso_013_tight_cap")(USOTightCapStrategy)
