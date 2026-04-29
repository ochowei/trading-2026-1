"""
EEM-013: MACD Histogram Zero-Cross + Pullback Hybrid Mean Reversion Strategy

Repo 首次 MACD 試驗。使用 MACD(12, 26, 9) 柱狀圖零軸上穿作為動量轉折訊號，
搭配 10 日回檔過濾（-3% ~ -7%）及 EEM 驗證有效的 WR + ClosePos 品質確認。
出場採對稱 TP/SL（TP+3%/SL-3%/20d），成交模型為隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_013_macd_histogram_mr.config import (
    EEM013Config,
    create_default_config,
)
from trading.experiments.eem_013_macd_histogram_mr.signal_detector import (
    EEM013SignalDetector,
)


class EEM013Strategy(ExecutionModelStrategy):
    """EEM MACD Histogram Zero-Cross + Pullback MR (EEM-013)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM013Config):
            print(
                f"  MACD: MACD({config.macd_fast}, {config.macd_slow}, {config.macd_signal})"
                " 柱狀圖零軸上穿"
            )
            print(
                f"  回檔過濾: {config.pullback_lookback}日高點回檔"
                f" [{config.pullback_cap:.0%}, {config.pullback_floor:.0%}]"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 過濾 (反向): ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" < {config.atr_ratio_max}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
