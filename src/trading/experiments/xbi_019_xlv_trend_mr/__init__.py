"""XBI XLV Sector Parent Trend Filter on VIX Bands MR (XBI-019)"""

from trading.experiments import register
from trading.experiments.xbi_019_xlv_trend_mr.strategy import XBI019XlvTrendMRStrategy

register("xbi_019_xlv_trend_mr")(XBI019XlvTrendMRStrategy)
