"""
FXI-002: BB Squeeze Breakout
(FXI 布林帶擠壓突破)

EEM-005 驗證有效的 BB Squeeze 框架移植至 FXI，測試突破策略在中國 EM ETF 上的效果。
加入 SMA(50) 上升斜率過濾，減少下行趨勢中的假突破。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_002_bb_squeeze_breakout.config import (
    FXI002Config,
    create_default_config,
)
from trading.experiments.fxi_002_bb_squeeze_breakout.signal_detector import (
    FXI002SignalDetector,
)


class FXI002Strategy(ExecutionModelStrategy):
    """FXI BB 擠壓突破 (FXI-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI002SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI002Config):
            print(f"  布林帶 (BB): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓偵測: {config.bb_squeeze_percentile_window} 日"
                f" {config.bb_squeeze_percentile:.0%} 百分位,"
                f" 近 {config.bb_squeeze_recent_days} 日"
            )
            print(f"  趨勢確認: SMA({config.sma_trend_period})")
            print(f"  趨勢斜率: SMA({config.sma_trend_period}) {config.sma_slope_lookback}日正斜率")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
