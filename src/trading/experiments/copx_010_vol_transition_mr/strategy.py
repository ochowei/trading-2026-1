"""
COPX-010: Post-Capitulation Vol-Transition Mean Reversion Strategy

基於 COPX-007 框架新增 2 日累計報酬過濾器，捕捉急跌後的減速階段進場，
濾除崩盤加速中的連續停損訊號。延伸 CIBR-012 Att3 的跨資產假設：
「2DD cap filter 可能適用於其他面對 BB lower + cap 混合模式的 US 板塊 ETF」。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_010_vol_transition_mr.config import (
    COPX010Config,
    create_default_config,
)
from trading.experiments.copx_010_vol_transition_mr.signal_detector import (
    COPX010SignalDetector,
)


class COPX010Strategy(ExecutionModelStrategy):
    """COPX-010：Post-Capitulation Vol-Transition MR"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX010Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            if config.twoday_return_cap > -0.5:
                print(f"  2 日累計報酬上限: >= {config.twoday_return_cap:.1%}（過濾崩盤加速中）")
            if config.twoday_return_floor > -0.5:
                print(
                    f"  2 日累計報酬下限: <= {config.twoday_return_floor:.1%}"
                    f"（要求真實 capitulation）"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
