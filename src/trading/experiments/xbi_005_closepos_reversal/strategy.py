"""
XBI-005: 回檔 + Williams %R + 反轉K線均值回歸策略
(XBI Pullback + Williams %R + Reversal Candlestick Strategy)

在 XBI-001 基礎上加入 ClosePos >= 40% 反轉K線確認。
IWM-005 驗證 ClosePos 在中低波動 ETF 是必要品質過濾器（移除後 WR 48.8%）。
XBI 日波動 ~2.0% 與 IWM 接近，測試此過濾器是否能改善 Part A Sharpe。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_005_closepos_reversal.config import (
    XBI005Config,
    create_default_config,
)
from trading.experiments.xbi_005_closepos_reversal.signal_detector import (
    XBI005SignalDetector,
)


class XBI005Strategy(ExecutionModelStrategy):
    """XBI-005：回檔 + Williams %R + 反轉K線均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI005Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  反轉K線: ClosePos >= {config.close_position_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
