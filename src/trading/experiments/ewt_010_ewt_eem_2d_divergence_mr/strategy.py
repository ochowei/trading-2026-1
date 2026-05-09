"""
EWT-010: EWT-EEM 2D Divergence Filter on Vol-Transition MR Strategy

在 EWT-009 Att3 完整框架（BB 下軌 + 10d 回檔上限 -8% + WR + ClosePos
+ ATR(5)/ATR(20) > 1.10 + 2DD floor <= -1.5%, TP+3.5%/SL-4%/20d/cd 10）之上
疊加「EWT-EEM 雙時框 (5d AND 60d) divergence 同時越界 → 過濾」作為 cross-asset
divergence regime gate。

策略方向：pair-divergence as macro regime gate（lesson #20 v3 family v3
dimensionality extension：1D → 2D AND）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_010_ewt_eem_2d_divergence_mr.config import (
    EWT010Config,
    create_default_config,
)
from trading.experiments.ewt_010_ewt_eem_2d_divergence_mr.signal_detector import (
    EWT010SignalDetector,
)


class EWT010Strategy(ExecutionModelStrategy):
    """EWT-010：EWT-EEM 2D divergence + EWT-009 Att3 Vol-Transition MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT010Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(
                f"  Capitulation: {config.capitulation_mode} <= {config.capitulation_threshold:.2%}"
            )
            print(
                f"  EWT-{config.eem_ticker} 2D divergence filter: 同時 "
                f"({config.rs_short_lookback}d_div >= {config.rs_short_threshold:+.2%}) "
                f"AND ({config.rs_long_lookback}d_div >= {config.rs_long_threshold:+.2%})"
                " → 過濾（EWT-010 核心新增：cross-asset divergence regime gate）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
