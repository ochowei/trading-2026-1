"""
COPX-006: RSI(2) 短期均值回歸策略
COPX RSI(2) Short-Term Mean Reversion Strategy

以 RSI(2) 極端超賣 + 2日急跌 + 20日回檔作為進場條件。
模仿 URA-004 的成功公式，與 COPX-003（WR+回檔）使用不同進場機制。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_006_pairs_fcx.config import (
    COPXRsi2Config,
    create_default_config,
)
from trading.experiments.copx_006_pairs_fcx.signal_detector import (
    COPXRsi2Detector,
)


class COPXPairsFCXStrategy(ExecutionModelStrategy):
    """COPX-006：RSI(2) 短期均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPXRsi2Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPXRsi2Config):
            print(f"  RSI 週期/門檻 (RSI): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日跌幅門檻 (2d decline): ≤ {config.two_day_decline_threshold:.0%}")
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback}日回檔"
                f" ≥ {abs(config.pullback_threshold):.0%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
