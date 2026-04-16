"""
INDA-003 Att3: 20日回檔 + 2日急跌均值回歸
(20-Day Pullback + 2-Day Decline Mean Reversion)

Att1/Att2 驗證 BB Squeeze 對 INDA 嚴重市場狀態依賴（Part A/B WR 差 47pp），
Att3 轉向均值回歸改進：20日回看（GLD 模板）+ 2日急跌（URA/USO 模板）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_003_bb_squeeze_breakout.config import (
    INDA003Config,
    create_default_config,
)
from trading.experiments.inda_003_bb_squeeze_breakout.signal_detector import (
    INDA003SignalDetector,
)


class INDA003Strategy(ExecutionModelStrategy):
    """INDA 20日回檔+2日急跌均值回歸 (INDA-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA003SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA003Config):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  2日急跌 (2-Day Decline): >= {abs(config.decline_threshold):.1%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
