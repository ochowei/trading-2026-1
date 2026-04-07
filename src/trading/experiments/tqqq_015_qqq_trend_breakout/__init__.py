"""TQQQ-015: QQQ Trend Breakout → Trade TQQQ (成交模型)"""

from trading.experiments import register
from trading.experiments.tqqq_015_qqq_trend_breakout.strategy import (
    TQQQQqqTrendBreakoutStrategy,
)

register("tqqq_015_qqq_trend_breakout")(TQQQQqqTrendBreakoutStrategy)
