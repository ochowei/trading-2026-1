"""INDA Broad-EM Macro-Context-Confirmed Vol-Transition MR 策略 (INDA-013)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_013_broad_em_confirmed_mr.config import (
    INDA013Config,
    create_default_config,
)
from trading.experiments.inda_013_broad_em_confirmed_mr.signal_detector import (
    INDA013SignalDetector,
)


class INDA013Strategy(ExecutionModelStrategy):
    """INDA-013：inda_010 框架 + broad-EM macro context confirmation gate"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA013Config):
            print(
                f"  回檔 ∈ [{config.pullback_cap:.0%}, {config.pullback_threshold:.0%}]"
                f" + WR({config.wr_period}) <= {config.wr_threshold}"
            )
            print(
                f"  ClosePos >= {config.close_position_threshold}"
                f" + ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日報酬 <= {config.drop_2d_floor:.0%}")
            if config.use_broad_em_gate:
                print(
                    f"  broad-EM 確認閘門: {config.broad_em_ticker}"
                    f" {config.eem_lookback}日報酬 <= {config.max_eem_return:.0%}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
