"""
GLD-013: Post-Capitulation Vol-Transition Mean Reversion Strategy

跨資產延伸 VGK-008 Att2 至商品 ETF 類別：在 BB 下軌+回檔上限混合進場框架上，
以「2 日報酬下限」（2DD floor）過濾「淺幅慢漂移」的弱 MR 訊號。

跨類別貢獻：首次於商品 ETF 驗證 Post-Capitulation Vol-Transition MR 模式。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_013_vol_transition_mr.config import (
    GLD013Config,
    create_default_config,
)
from trading.experiments.gld_013_vol_transition_mr.signal_detector import (
    GLD013SignalDetector,
)


class GLD013Strategy(ExecutionModelStrategy):
    """GLD Post-Capitulation Vol-Transition MR (GLD-013)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD013Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（商品 ETF 溫和崩盤隔離）"
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
                f"  2 日報酬下限: <= {config.twoday_return_floor:.1%}（排除淺幅慢漂移的弱 MR 訊號）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
