"""
FCX-012: Donchian Lower Washout + Intraday Reversal Mean Reversion Strategy

**Repo 首次「Donchian Lower + 日內反轉」組合作為 MR 主進場訊號試驗**。
目標為改善 FCX-004（BB Squeeze Breakout，min 0.41）與 FCX-001
（grandfathered，Sharpe 0.43/0.74 但 A/B 累計差 72%）的 Part A/B 平衡性。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_012_donchian_low_washout.config import (
    FCX012Config,
    create_default_config,
)
from trading.experiments.fcx_012_donchian_low_washout.signal_detector import (
    FCX012SignalDetector,
)


class FCX012Strategy(ExecutionModelStrategy):
    """FCX Donchian Lower Washout + Intraday Reversal MR (FCX-012)"""

    slippage_pct: float = 0.0015  # 0.15%（FCX 高波動個股標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX012Config):
            print(
                f"  Donchian Low: {config.donchian_period} 日最低 Low"
                f"，Close 距低點 <= {config.close_near_low_threshold:.1%}"
            )
            if config.require_washout_day:
                print(
                    f"  Washout 確認: 今日或過去 {config.washout_lookback_days}"
                    " 日內 Low = Donchian Low"
                )
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}（日內反轉）")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" >= {config.atr_ratio_threshold}"
            )
            print(
                f"  60 日回撤範圍: [{config.drawdown_lower:.0%}, {config.drawdown_upper:.0%}]"
                "（中等深度）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
