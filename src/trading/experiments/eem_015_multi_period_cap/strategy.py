"""
EEM Multi-Period Capitulation-Strength Filter MR Strategy (EEM-015)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_015_multi_period_cap.config import (
    EEM015Config,
    create_default_config,
)
from trading.experiments.eem_015_multi_period_cap.signal_detector import (
    EEM015SignalDetector,
)


class EEM015Strategy(ExecutionModelStrategy):
    """EEM-015：EEM-014 + 3DD cap（INDA-011 Att3 跨資產驗證）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM015SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM015Config):
            print(f"  BB({config.bb_period}, {config.bb_std}) 下軌進場（mean reversion）")
            print(f"  10日回檔上限: >= {config.pullback_cap:.1%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  ClosePos >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2日跌幅 floor: 2DD <= {config.twoday_return_floor:.1%}")
            print(f"  3日跌幅 cap: 3DD >= {config.threeday_return_cap:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
