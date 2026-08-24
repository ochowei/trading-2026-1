"""DIA Strict-Bull-Regime Trend Pullback Continuation (DIA-013)"""

from trading.experiments import register
from trading.experiments.dia_013_trend_regime_pullback.strategy import DIA013Strategy

register("dia_013_trend_regime_pullback")(DIA013Strategy)
