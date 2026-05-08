"""
EEM-019: EEM-FXI Divergence-Gated Vol-Transition MR Strategy

在 EEM-014 Att2 框架（min(A,B) 0.56）之上新增「EEM vs FXI 10 日相對強度上限」
過濾，作為 cross-asset pair-divergence regime gate（lesson #20 v3 變體）。
FXI（中國大型股 ETF）為 EEM 內 ~30% 權重的最大單一國家成分。

預期效果：
- 過濾 Part B 2025-11-19 SL（美中貿易摩擦升溫 → 預期 EEM_10d - FXI_10d > 0
  反映 China-specific 結構性疲弱潛伏）
- 過濾 Part A 2021-07-08 SL（DiDi ADR 監管衝擊 → 預期 EEM_10d - FXI_10d 偏正向）
- 保留 broad EM/risk-off rebound TPs（EEM 與 FXI 同步深跌期）
- 預期 Part B Sharpe 0.56 → 1.0+，Part A Sharpe 0.73 → 1.0+
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_019_eem_fxi_divergence_mr.config import (
    EEM019Config,
    create_default_config,
)
from trading.experiments.eem_019_eem_fxi_divergence_mr.signal_detector import (
    EEM019DivergenceDetector,
)


class EEM019Strategy(ExecutionModelStrategy):
    """EEM-019: EEM-FXI Divergence-Gated Vol-Transition MR"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM019DivergenceDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM019Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(f"  回檔上限: {config.pullback_lookback}日高點回檔 >= {config.pullback_cap:.0%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日急跌下限: <= {config.twoday_return_floor:.1%}")
            print(
                f"  EEM-{config.fxi_ticker} rel: {config.rel_lookback}日報酬差"
                f" <= {config.max_rel_return:+.2%} (ceiling/cap)"
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)
