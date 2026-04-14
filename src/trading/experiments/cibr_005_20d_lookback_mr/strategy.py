"""
CIBR 20日回看窗口均值回歸策略 (CIBR 20-Day Lookback Mean Reversion Strategy)

結構性變更回看窗口（10→20日）與 WR 週期（10→14），
測試更長期回檔模式對 Part A 績效的影響。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_005_20d_lookback_mr.config import (
    CIBR20DLookbackMRConfig,
    create_default_config,
)
from trading.experiments.cibr_005_20d_lookback_mr.signal_detector import (
    CIBR20DLookbackMRSignalDetector,
)


class CIBR20DLookbackMRStrategy(ExecutionModelStrategy):
    """CIBR-005：20日回看窗口均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR20DLookbackMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR20DLookbackMRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
