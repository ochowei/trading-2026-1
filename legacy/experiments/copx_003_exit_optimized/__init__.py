"""COPX 20日回檔 + Williams %R + 出場優化 均值回歸 (COPX-003)"""

from trading.experiments import register
from trading.experiments.copx_003_exit_optimized.strategy import (
    COPXExitOptimizedStrategy,
)

register("copx_003_exit_optimized")(COPXExitOptimizedStrategy)
