"""VGK RSI(2) 延長持倉均值回歸 (VGK-003)"""

from trading.experiments import register
from trading.experiments.vgk_003_extended_hold_rsi2.strategy import VGK003Strategy

register("vgk_003_extended_hold_rsi2")(VGK003Strategy)
