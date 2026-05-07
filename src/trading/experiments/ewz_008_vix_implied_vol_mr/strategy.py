"""EWZ ^VIX Forward-Looking Implied-Vol Regime-Gated MR 策略 (EWZ-008)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewz_008_vix_implied_vol_mr.config import (
    EWZ008Config,
    create_default_config,
)
from trading.experiments.ewz_008_vix_implied_vol_mr.signal_detector import (
    EWZ008SignalDetector,
)


class EWZ008Strategy(ExecutionModelStrategy):
    """EWZ-008：EWZ-007 Att3 框架 + ^VIX forward-looking implied vol regime gate"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWZ008SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWZ008Config):
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
                f"  VIX implied-vol gate: {config.vix_ticker} "
                f"{config.vix_direction_lookback}d change <= {config.max_vix_change:+.1f}"
            )
            print(f"  VIX level cap: {config.vix_ticker} Close <= {config.max_vix_level:.1f}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
