"""
VGK-009: EURUSD Direction Filter on Vol-Transition MR Strategy

延伸 VGK-008 Att2 框架，新增「EUR/USD 方向過濾」（bilateral FX direction
filter）。為 repo 第 2 次 bilateral FX direction 跨資產應用（繼 EWJ-006
USDJPY 後），擴展 lesson #24 family v8 至歐洲已開發 ETF。

出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_009_eurusd_direction_mr.config import (
    VGK009Config,
    create_default_config,
)
from trading.experiments.vgk_009_eurusd_direction_mr.signal_detector import (
    VGK009EURUSDDirectionDetector,
)


class VGK009Strategy(ExecutionModelStrategy):
    """VGK-009: EURUSD Direction-Gated Vol-Transition MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGK009EURUSDDirectionDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGK009Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
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
            print(f"  2 日報酬下限: <= {config.twoday_return_floor:.1%}（VGK-008 Att2 2DD floor）")
            print(
                f"  EUR/USD 方向: {config.eurusd_lookback}日報酬"
                f" >= {config.min_eurusd_change:.2%}（{config.eurusd_ticker}）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
