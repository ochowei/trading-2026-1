"""
IBIT-009: Post-Capitulation Vol-Transition MR
(IBIT Gap-Down + Intraday Reversal + 2-Day Decline Floor MR)

進場使用 IBIT-006 Att2 五項條件 + 2-Day Decline Floor（後 capitulation 過濾），
出場使用固定對稱 TP/SL（TP +4.5%/SL -4.0%）。成交模型採隔日開盤市價。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ibit_009_post_cap_vol_transition_mr.config import (
    IBIT009Config,
    create_default_config,
)
from trading.experiments.ibit_009_post_cap_vol_transition_mr.signal_detector import (
    IBIT009SignalDetector,
)


class IBIT009Strategy(ExecutionModelStrategy):
    """IBIT-009：Post-Capitulation Vol-Transition MR"""

    slippage_pct: float = 0.0015  # 0.15% 加密貨幣 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IBIT009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IBIT009Config):
            print(f"  隔夜跳空 (Gap): Gap <= {config.gap_threshold:.1%}")
            print("  日內反轉: Close > Open")
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  2日累計報酬下限 (2DD floor): 2DD <= {config.twoday_floor:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
