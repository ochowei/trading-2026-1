"""
FXI-003: Volatility-Adaptive Mean Reversion
(FXI 波動率自適應均值回歸)

在 FXI-001 的 pullback+WR 基礎上加入 ATR 波動率急升過濾與 ClosePos 反轉確認。
參考 IWM-011 和 COPX-007 的成功框架。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_003_vol_adaptive_mr.config import (
    FXI003Config,
    create_default_config,
)
from trading.experiments.fxi_003_vol_adaptive_mr.signal_detector import (
    FXI003SignalDetector,
)


class FXI003Strategy(ExecutionModelStrategy):
    """FXI 波動率自適應均值回歸 (FXI-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI003SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI003Config):
            print(f"  回檔門檻: {config.pullback_lookback}日高點 ≥ {config.pullback_threshold:.0%}")
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  ClosePos 確認: ≥ {config.closepos_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
