"""GLD 20日回檔 + WR + 反轉K線 + 追蹤停損 (GLD-008)"""

from trading.experiments import register
from trading.experiments.gld_008_rsi2_trailing.strategy import GLD008Strategy

register("gld_008_rsi2_trailing")(GLD008Strategy)
