"""
EEM-017: EEM-EFA Cross-Asset Divergence Filter on Vol-Transition MR Strategy

延伸 EEM-014 Att2 框架，新增「EEM-EFA 10 日相對強度發散」過濾器
（broad-EM-vs-broad-DM divergence regime gate）。
出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_017_eem_efa_divergence_mr.config import (
    EEM017Config,
    create_default_config,
)
from trading.experiments.eem_017_eem_efa_divergence_mr.signal_detector import (
    EEM017DivergenceDetector,
)


class EEM017Strategy(ExecutionModelStrategy):
    """EEM-017: EEM-EFA Divergence-Gated Vol-Transition MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM017DivergenceDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM017Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日報酬下限: <= {config.twoday_return_floor:.2%}（同 EEM-014 Att2 甜蜜點）")
            print(
                f"  EEM-EFA 發散 (floor): {config.rel_lookback}日 EEM 報酬 - EFA 報酬"
                f" >= {config.min_rel_diff:.2%}"
                f"（broad-EM-vs-broad-DM divergence regime gate）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
