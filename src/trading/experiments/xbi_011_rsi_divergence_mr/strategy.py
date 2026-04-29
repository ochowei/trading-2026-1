"""
XBI-011: RSI Bullish Divergence + Pullback+WR+ClosePos Mean Reversion Strategy

在 XBI-005 基礎上加入 RSI(14) bullish hook 過濾器（SIVR-015 驗證模式）。
XBI-005 Part A Sharpe 0.36 / Part B 0.65（A/B 訊號比 3.5:1，累計差 57%），
測試 bullish hook 過濾器是否能移除 Part A 的持續下跌訊號，改善 A/B 平衡。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_011_rsi_divergence_mr.config import (
    XBI011Config,
    create_default_config,
)
from trading.experiments.xbi_011_rsi_divergence_mr.signal_detector import (
    XBI011SignalDetector,
)


class XBI011Strategy(ExecutionModelStrategy):
    """XBI-011：RSI Bullish Divergence + Pullback+WR+ClosePos 均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI011Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  反轉K線: ClosePos >= {config.close_position_threshold:.0%}")
            print(
                f"  RSI({config.rsi_period}) Bullish Hook: "
                f"lookback {config.rsi_hook_lookback} 日 / delta ≥ {config.rsi_hook_delta} / "
                f"near-low RSI ≤ {config.rsi_hook_max_min}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
