"""
XBI-010: BB Lower Band + Pullback Cap Hybrid Mean Reversion Strategy

使用 BB(20, 1.5) 下軌觸及 + 10日高點回檔上限 -12% 混合進場，
搭配 WR + ClosePos 雙重品質過濾。
出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。

XBI 2.0% 日波動處於 ClosePos 有效邊界，但 ATR 過濾在 XBI-009 已驗證無效
（日波動達 ATR 有效邊界上限），故混合進場採雙重而非三重品質過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_010_bb_lower_pullback_cap.config import (
    XBI010Config,
    create_default_config,
)
from trading.experiments.xbi_010_bb_lower_pullback_cap.signal_detector import (
    XBI010SignalDetector,
)


class XBI010Strategy(ExecutionModelStrategy):
    """XBI-010：BB 下軌 + 回檔上限混合進場"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI010Config):
            print(
                f"  進場觸發 (OR): BB({config.bb_period}, {config.bb_std}) 下軌 OR"
                f" {config.pullback_lookback}日回檔 <= {config.pullback_entry_threshold:.0%}"
            )
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
