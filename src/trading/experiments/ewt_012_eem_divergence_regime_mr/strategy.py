"""EWT–EEM Cross-Asset Divergence Regime-Gated MR 策略 (EWT-012)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_012_eem_divergence_regime_mr.config import (
    EWT012Config,
    create_default_config,
)
from trading.experiments.ewt_012_eem_divergence_regime_mr.signal_detector import (
    EWT012SignalDetector,
)


class EWT012EemDivergenceRegimeMRStrategy(ExecutionModelStrategy):
    """EWT-012：EWT-009 Att3 + EWT–EEM 跨資產 divergence regime gate"""

    slippage_pct: float = 0.001  # 0.1%（EWT 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT012Config):
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
            if config.use_divergence_gate:
                print(
                    f"  Divergence gate: EWT−{config.divergence_ticker} "
                    f"{config.divergence_lookback}d return "
                    f"{'<=' if config.divergence_mode == 'ceiling' else '>='} "
                    f"{config.divergence_threshold:+.2%} ({config.divergence_mode})"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
