"""
CIBR-004 Att2: 動量強化均值回歸策略

在 CIBR-002 pullback+WR+ATR 基礎上新增 2日急跌過濾 + 非對稱出場優化。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_004_rsi2_vol_adaptive.config import (
    CIBR004Config,
    create_default_config,
)
from trading.experiments.cibr_004_rsi2_vol_adaptive.signal_detector import (
    CIBR004SignalDetector,
)


class CIBRRSI2VolAdaptiveStrategy(ExecutionModelStrategy):
    """CIBR-004: 動量強化均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR004Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(
                f"  2日跌幅: {config.decline_lookback}日累計跌幅"
                f" >= {abs(config.decline_threshold):.1%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
