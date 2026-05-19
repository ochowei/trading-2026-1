"""
EWZ-010: EWZ–BRL Currency-Regime-Gated Vol-Transition MR Strategy

在 EWZ-009 Att1 框架（min(A,B) 1.50，七條件 MR）之上新增第八條件
「EWZ–BRL 貨幣 regime gate」（GLD-016 USD-regime / FXI-015 CNY-regime
形式）。predict→confirm 預測 documented-failure：殘餘 binding Part A SL
2019-03-25 於 BRL 各維度與 9 winners 完全交錯，無 ≥15pp robust plateau。

Uses ExecutionModelBacktester (next-open + 0.1% slippage + pessimistic
intrabar)。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewz_010_brl_regime_mr.config import (
    EWZ010Config,
    create_default_config,
)
from trading.experiments.ewz_010_brl_regime_mr.signal_detector import (
    EWZ010SignalDetector,
)


class EWZ010BrlRegimeMRStrategy(ExecutionModelStrategy):
    """EWZ-010：EWZ-009 Att1 + EWZ–BRL 貨幣 regime gate"""

    slippage_pct: float = 0.001  # 0.1%（EWZ 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWZ010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWZ010Config):
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
            if config.use_brl_ceiling:
                print(
                    f"  BRL CEILING gate: {config.brl_ticker} "
                    f"{config.brl_lookback}d return <= {config.max_brl_return:+.1%}"
                )
            if config.use_brl_divergence:
                print(
                    f"  BRL DIVERGENCE gate: EWZ−{config.brl_ticker} "
                    f"{config.brl_lookback}d return >= {config.min_relative_return:+.1%}"
                )
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)
