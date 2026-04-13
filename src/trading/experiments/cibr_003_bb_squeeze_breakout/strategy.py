"""
CIBR BB 擠壓突破策略 (CIBR BB Squeeze Breakout Strategy)

波動率壓縮後向上突破布林帶上軌，配合 SMA(50) 趨勢確認。
出場使用固定止盈/停損（不使用追蹤停損）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_003_bb_squeeze_breakout.config import (
    CIBRBBSqueezeConfig,
    create_default_config,
)
from trading.experiments.cibr_003_bb_squeeze_breakout.signal_detector import (
    CIBRBBSqueezeSignalDetector,
)


class CIBRBBSqueezeStrategy(ExecutionModelStrategy):
    """CIBR-003：BB 擠壓突破"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBRBBSqueezeSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBRBBSqueezeConfig):
            print(f"  布林帶 (BB): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓偵測: {config.bb_squeeze_percentile:.0%} 百分位"
                f" / {config.bb_squeeze_percentile_window} 日回看"
                f" / 近 {config.bb_squeeze_recent_days} 日"
            )
            print(f"  趨勢確認: SMA({config.sma_trend_period})")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
