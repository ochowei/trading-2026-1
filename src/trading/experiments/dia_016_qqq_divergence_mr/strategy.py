"""
DIA-016: DIA-QQQ Cross-Asset Divergence CEILING Regime-Gated MR Strategy

在 DIA-012 Att2 框架（min(A,B)† 1.31，DIA 全域最佳）之上新增「DIA vs IWM
10 日相對強度上限（CEILING）」，作為 cross-asset divergence regime gate
（lesson #20 v3 CEILING 方向，鏡像 NVDA-021 / INDA-012）。

預期效果：
- 過濾 2022-01-18 唯一 Part A SL（relIWM_10d +4.53%，全 Part A 最高）
- 保留全部 11 Part A 獲利訊號（10 TP + 1 expiry，max relIWM_10d +2.77%）
- Part B 完全不受影響（3 訊號 relIWM_10d <= +2.21% < +3.5%）
- 預期 Part A 12→11 訊號 WR 91.7%→100%，Sharpe 1.31 → 顯著提升
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_016_qqq_divergence_mr.config import (
    DIA016Config,
    create_default_config,
)
from trading.experiments.dia_016_qqq_divergence_mr.signal_detector import (
    DIA016SignalDetector,
)


class DIA016Strategy(ExecutionModelStrategy):
    """DIA-QQQ Divergence CEILING Regime-Gated MR (DIA-016)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA016Config):
            print(f"  RSI 期數: {config.rsi_period} / 門檻 < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(f"  收盤位置: >= {config.close_position_threshold:.0%} of day range")
            print(f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}")
            print(f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}")
            print(
                f"  DIA-{config.anchor_ticker} rel CEILING:"
                f" {config.rel_lookback}日報酬差 <= {config.max_rel_return:+.2%}"
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)
