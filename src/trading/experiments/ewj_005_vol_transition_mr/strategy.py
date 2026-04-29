"""
EWJ-005: Post-Capitulation Vol-Transition MR Strategy

延伸 EWJ-003 Att3 框架，新增「Capitulation strength filter」。
出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewj_005_vol_transition_mr.config import (
    EWJ005Config,
    create_default_config,
)
from trading.experiments.ewj_005_vol_transition_mr.signal_detector import (
    EWJ005SignalDetector,
)


class EWJ005Strategy(ExecutionModelStrategy):
    """EWJ-005: Post-Capitulation Vol-Transition MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWJ005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWJ005Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(
                f"  Capitulation: {config.capitulation_mode} <= {config.capitulation_threshold:.2%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
