"""
EWJ-006: USDJPY Direction Filter on Vol-Transition MR Strategy

延伸 EWJ-005 Att2 框架，新增「USDJPY 方向過濾」。
出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewj_006_usdjpy_direction_mr.config import (
    EWJ006Config,
    create_default_config,
)
from trading.experiments.ewj_006_usdjpy_direction_mr.signal_detector import (
    EWJ006USDJPYDirectionDetector,
)


class EWJ006Strategy(ExecutionModelStrategy):
    """EWJ-006: USDJPY Direction-Gated Vol-Transition MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWJ006USDJPYDirectionDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWJ006Config):
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
            print(
                f"  USDJPY 方向: {config.usdjpy_lookback}日報酬"
                f" <= {config.max_usdjpy_change:.2%}（{config.usdjpy_ticker}）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
