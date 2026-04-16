"""EWT 2-Day Crash Filter + Asymmetric Exit MR (EWT-004)"""

from trading.experiments import register
from trading.experiments.ewt_004_crash_filter_asymmetric.strategy import EWT004Strategy

register("ewt_004_crash_filter_asymmetric")(EWT004Strategy)
