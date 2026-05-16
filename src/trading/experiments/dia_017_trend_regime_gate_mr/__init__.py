"""DIA Buffered Multi-Week SMA Trend-Regime-Gated MR (DIA-017)"""

from trading.experiments import register
from trading.experiments.dia_017_trend_regime_gate_mr.strategy import DIA017Strategy

register("dia_017_trend_regime_gate_mr")(DIA017Strategy)
