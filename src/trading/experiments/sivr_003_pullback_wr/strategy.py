"""
SIVR 回檔 + Williams %R 均值回歸策略 (SIVR Pullback + Williams %R Mean Reversion Strategy)
進場使用 10 日高點回檔 + Williams %R 雙重確認，出場使用固定止盈/停損。
不使用追蹤停損（SIVR-002 已驗證追蹤停損在高波動白銀上失敗）。

Entry uses pullback from 10-day high + Williams %R confirmation.
Exit uses fixed TP/SL (no trailing stop - proven ineffective for SIVR in SIVR-002).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_003_pullback_wr.config import (
    SIVRPullbackWRConfig,
    create_default_config,
)
from trading.experiments.sivr_003_pullback_wr.signal_detector import (
    SIVRPullbackWRSignalDetector,
)


class SIVRPullbackWRStrategy(ExecutionModelStrategy):
    """SIVR-003：回檔 + Williams %R 均值回歸"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較 GLD 低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRPullbackWRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRPullbackWRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
