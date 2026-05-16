"""
DIA-017: Buffered Multi-Week SMA Trend-Regime-Gated MR Strategy

在 DIA-012 Att2 框架（min(A,B)† 1.31）之上新增 lesson #22 buffered
multi-week SMA 趨勢 regime 閘門（cross-strategy port from XBI-015）。
pre-analysis 預期 reverse-selection 結構性失敗，建立 lesson #22 family
失敗邊界（low-vol broad-index capitulation MR 之 bear-rally winner 被
bull-regime gate 反向移除）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_017_trend_regime_gate_mr.config import (
    DIA017Config,
    create_default_config,
)
from trading.experiments.dia_017_trend_regime_gate_mr.signal_detector import (
    DIA017SignalDetector,
)


class DIA017Strategy(ExecutionModelStrategy):
    """DIA Buffered Multi-Week SMA Trend-Regime-Gated MR (DIA-017)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA017SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA017Config):
            print(f"  RSI 期數: {config.rsi_period} / 門檻 < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(f"  收盤位置: >= {config.close_position_threshold:.0%} of day range")
            print(f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}")
            print(f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}")
            print(
                f"  lesson #22 SMA regime: SMA({config.sma_fast})"
                f" >= {config.regime_k:.3f} × SMA({config.sma_slow})"
                + (f" AND Close > SMA({config.sma_long})" if config.require_above_long else "")
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)
