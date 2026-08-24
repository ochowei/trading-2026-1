"""DIA RSI(2) 寬獲利目標均值回歸 (DIA-004)"""

from trading.experiments import register
from trading.experiments.dia_004_wider_tp.strategy import (
    DIARsi2WiderTPStrategy,
)

register("dia_004_wider_tp")(DIARsi2WiderTPStrategy)
