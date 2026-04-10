"""
FCX-008: Trend Pullback to SMA(50) (趨勢跟蹤回檔)
"""

from trading.experiments import register
from trading.experiments.fcx_008_trend_pullback.strategy import FCXTrendPullbackStrategy

register("fcx_008_trend_pullback")(FCXTrendPullbackStrategy)
