"""COPX 深度回撤均值回歸 (COPX-002)"""

from trading.experiments import register
from trading.experiments.copx_002_deep_drawdown.strategy import (
    COPXDeepDrawdownStrategy,
)

register("copx_002_deep_drawdown")(COPXDeepDrawdownStrategy)
