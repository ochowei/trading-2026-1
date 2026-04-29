"""
CIBR-010: NR7 Volatility Contraction + Pullback Mean Reversion Strategy

在 pullback+WR 超賣情境下，疊加 NR7（Narrowest Range 7）波動率壓縮過濾器，
捕捉「賣壓衰竭 + 波動率壓縮」的 coiled-spring 均值回歸機會。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_010_nr7_pullback_mr.config import (
    CIBR010Config,
    create_default_config,
)
from trading.experiments.cibr_010_nr7_pullback_mr.signal_detector import (
    CIBR010SignalDetector,
)


class CIBR010Strategy(ExecutionModelStrategy):
    """CIBR-010：NR7 Volatility Contraction + Pullback MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR010Config):
            print(
                f"  回檔: {config.pullback_lookback}日高點回檔"
                f" <= {config.pullback_threshold * 100:.1f}%"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  NR 窗口: 今日 TR 為近 {config.nr_window} 日最小")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            if config.use_atr_filter:
                print(
                    f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                    f" > {config.atr_ratio_threshold}"
                )
            else:
                print("  ATR 過濾: 關閉（與 NR7 結構性衝突）")
            if config.use_decline_filter:
                print(
                    f"  {config.decline_lookback}日跌幅: <= {config.decline_threshold * 100:.1f}%"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
