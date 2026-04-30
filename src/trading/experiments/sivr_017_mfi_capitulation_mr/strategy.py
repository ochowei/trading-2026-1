"""
SIVR-017 Money Flow Index Capitulation Mean Reversion Strategy
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_017_mfi_capitulation_mr.config import (
    SIVR017Config,
    create_default_config,
)
from trading.experiments.sivr_017_mfi_capitulation_mr.signal_detector import (
    SIVRMFICapitulationMRSignalDetector,
)


class SIVRMFICapitulationMRStrategy(ExecutionModelStrategy):
    """SIVR-017：MFI volume-weighted capitulation 過濾於 SIVR-005 基礎進場"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRMFICapitulationMRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVR017Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%}"
                f" ~ {abs(config.pullback_cap):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            if config.mfi_hook_enabled:
                print(
                    f"  Money Flow Index Bullish Hook: "
                    f"MFI({config.mfi_period}) lookback {config.mfi_hook_lookback} 日 / "
                    f"delta ≥ {config.mfi_hook_delta} / "
                    f"near-low MFI ≤ {config.mfi_hook_max_min}"
                )
            else:
                print(
                    f"  Money Flow Index: MFI({config.mfi_period}) <= {config.mfi_threshold}"
                    f"（volume-weighted oversold）"
                )
            if config.rsi_hook_enabled:
                print(
                    f"  RSI({config.rsi_period}) Bullish Hook (疊加): "
                    f"lookback {config.rsi_hook_lookback} 日 / "
                    f"delta ≥ {config.rsi_hook_delta} / "
                    f"near-low RSI ≤ {config.rsi_hook_max_min}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
