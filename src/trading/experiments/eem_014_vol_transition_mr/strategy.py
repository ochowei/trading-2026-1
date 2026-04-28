"""
EEM-014: Post-Capitulation Vol-Transition Mean Reversion Strategy

跨資產延伸 CIBR-012 Att3 至 broad EM ETF：在 EEM-012 Att3 BB 下軌+回檔上限
混合進場框架上，新增「2 日急跌上限」（2DD cap）過濾「崩盤加速中」進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_014_vol_transition_mr.config import (
    EEM014Config,
    create_default_config,
)
from trading.experiments.eem_014_vol_transition_mr.signal_detector import (
    EEM014SignalDetector,
)


class EEM014Strategy(ExecutionModelStrategy):
    """EEM Post-Capitulation Vol-Transition MR (EEM-014)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM014Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= -{abs(config.pullback_cap):.0%}（EM 崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(
                f"  2 日報酬下限: <= {config.twoday_return_floor:.1%}"
                "（排除淺幅慢漂移的弱 MR 訊號，repo 第 2 次 2DD floor 驗證）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
