"""CIBR Volatility-Level-Regime-Gated BB-Lower Pullback-Cap MR 策略 (CIBR-016)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_016_vol_level_gate_mr.config import (
    CIBR016Config,
    create_default_config,
)
from trading.experiments.cibr_016_vol_level_gate_mr.signal_detector import (
    CIBR016SignalDetector,
)


class CIBR016Strategy(ExecutionModelStrategy):
    """CIBR-016：CIBR-008 框架 + 絕對波動率 LEVEL regime 閘門（執行模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR016Config):
            print(
                f"  BB({config.bb_period}, {config.bb_std}) 下軌 + 10日回檔"
                f" >= {config.pullback_cap:.0%}"
            )
            print(
                f"  WR({config.wr_period}) <= {config.wr_threshold}"
                f" + ClosePos >= {config.close_pos_threshold}"
            )
            print(
                f"  ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold} (相對 acceleration)"
            )
            if config.use_vol_level_gate:
                print(
                    f"  絕對波動率 LEVEL 閘門: ATR({config.atr_level_period})/Close"
                    f" <= {config.max_atr_pct:.1%}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
