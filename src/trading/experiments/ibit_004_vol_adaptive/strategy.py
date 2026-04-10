"""
IBIT-004: 波動率自適應 / 2日急跌均值回歸策略
(IBIT Volatility-Adaptive / 2-Day Drop Mean Reversion Strategy)

基於 IBIT-001 + 2日急跌過濾。ATR 過濾在 Att1/Att2 失敗。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ibit_004_vol_adaptive.config import (
    IBIT004Config,
    create_default_config,
)
from trading.experiments.ibit_004_vol_adaptive.signal_detector import (
    IBIT004SignalDetector,
)


class IBIT004Strategy(ExecutionModelStrategy):
    """IBIT-004：波動率自適應 / 2日急跌均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 加密貨幣 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IBIT004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IBIT004Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  2日急跌過濾: ≤ {config.two_day_drop_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
