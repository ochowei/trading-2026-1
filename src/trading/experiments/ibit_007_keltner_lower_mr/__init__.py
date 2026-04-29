"""IBIT Keltner 通道下軌 + 回檔 + 反轉 K 線均值回歸 (IBIT-007)"""

from trading.experiments import register
from trading.experiments.ibit_007_keltner_lower_mr.strategy import (
    IBIT007Strategy,
)

register("ibit_007_keltner_lower_mr")(IBIT007Strategy)
