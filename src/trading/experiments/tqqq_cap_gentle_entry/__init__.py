"""
TQQQ 溫和放寬進場策略 (TQQQ Gentle Entry Relaxation)
僅放寬 drawdown 門檻 + TQQQ-008 優化出場。
"""

from trading.experiments import register
from trading.experiments.tqqq_cap_gentle_entry.strategy import TQQQCapGentleEntryStrategy

register("tqqq_cap_gentle_entry")(TQQQCapGentleEntryStrategy)
