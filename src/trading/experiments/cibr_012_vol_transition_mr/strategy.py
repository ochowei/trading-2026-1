"""
CIBR-012: Post-Capitulation Vol-Transition Mean Reversion Strategy

核心創新：替換 CIBR-008 的單一 ATR 過濾為「recent peak + current settling」雙條件，
以捕捉急跌後的穩定期進場時機，濾除急跌中期的連續停損訊號。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_012_vol_transition_mr.config import (
    CIBR012Config,
    create_default_config,
)
from trading.experiments.cibr_012_vol_transition_mr.signal_detector import (
    CIBR012SignalDetector,
)


class CIBR012Strategy(ExecutionModelStrategy):
    """CIBR-012：Post-Capitulation Vol-Transition MR"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR012Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" <= {abs(config.pullback_cap):.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 今日過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_today_threshold}（signal-day panic）"
            )
            print(
                f"  2 日報酬上限: >= {config.twoday_return_cap:.1%}"
                f"（排除 in-crash acceleration 進場）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
