"""
INDA-012: INDA-EEM RS Divergence Filter on Multi-Period Capitulation MR Strategy

在 INDA-011 Att3 完整框架（10d 回檔 + WR + ClosePos + ATR>1.15 + 2DD floor +
3DD cap）之上疊加「INDA - EEM N 日報酬差 <= max_rs_excess」過濾，作為
cross-asset divergence regime gate。

策略方向：pair-divergence as macro regime gate（lesson #20 v3）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_012_inda_eem_rs60d_divergence_mr.config import (
    INDA012Config,
    create_default_config,
)
from trading.experiments.inda_012_inda_eem_rs60d_divergence_mr.signal_detector import (
    INDA012SignalDetector,
)


class INDA012Strategy(ExecutionModelStrategy):
    """INDA-012：INDA-EEM RS divergence + INDA-011 多週期 capitulation MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA012Config):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日急跌下限: <= {config.drop_2d_floor:.1%}（沿用 INDA-010 Att3）")
            print(f"  3 日急跌上限: >= {config.drop_3d_cap:.1%}（沿用 INDA-011 Att3）")
            print(
                f"  INDA-{config.eem_ticker} RS 過濾: {config.rs_lookback}日報酬差"
                f" <= {config.max_rs_excess:+.2%}"
                "（INDA-012 核心新增：cross-asset divergence regime gate）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
