"""
CIBR-004: RSI(2) 波動率自適應均值回歸策略

測試 RSI(2) 框架在美國板塊 ETF（CIBR, 1.53% 日波動）的有效性。
RSI(2) 已在 SPY/DIA/IWM/VOO 等美國指數 ETF 驗證有效，
但尚未在美國板塊 ETF 上測試。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_004_rsi2_vol_adaptive.config import (
    CIBRRSI2Config,
    create_default_config,
)
from trading.experiments.cibr_004_rsi2_vol_adaptive.signal_detector import (
    CIBRRSI2SignalDetector,
)


class CIBRRSI2VolAdaptiveStrategy(ExecutionModelStrategy):
    """CIBR-004: RSI(2) 波動率自適應均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBRRSI2SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBRRSI2Config):
            print(f"  RSI: RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  2日跌幅: {config.decline_lookback}日累計跌幅"
                f" >= {abs(config.decline_threshold):.1%}"
            )
            print(f"  Close Position: >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
