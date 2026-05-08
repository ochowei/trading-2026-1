"""
EWZ-009: EWZ-EEM Divergence-Gated Vol-Transition MR Strategy

在 EWZ-007 Att3 框架（min(A,B) 0.95）之上新增「EWZ vs EEM 10 日相對強度上限」
過濾，作為 cross-asset pair-divergence regime gate（lesson #20 v3 變體）。

預期效果：
- 過濾 2020-01-31 SL（rel_10d +3.78pp，唯一 > +2.5pp 訊號）
- 保留全部 9 Part A TPs（max rel_10d +2.12pp）
- Part B 完全不受影響（max rel_10d -0.54pp）
- 預期 Part A WR 81.8% → 90%，Sharpe 0.95 → ~1.2
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewz_009_ewz_eem_divergence_mr.config import (
    EWZ009Config,
    create_default_config,
)
from trading.experiments.ewz_009_ewz_eem_divergence_mr.signal_detector import (
    EWZ009SignalDetector,
)


class EWZ009Strategy(ExecutionModelStrategy):
    """EWZ-009: EWZ-EEM Divergence-Gated Vol-Transition MR"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWZ009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWZ009Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(f"  回檔上限: {config.pullback_lookback}日高點回檔 >= {config.pullback_cap:.0%}")
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
                f"  EWZ-{config.eem_ticker} rel: {config.rel_lookback}日報酬差"
                f" <= {config.max_rel_return:+.2%}"
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)
