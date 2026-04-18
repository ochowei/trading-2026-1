"""
COPX-009: RSI Bullish Divergence + Pullback+WR+ATR Mean Reversion Strategy

基於 COPX-007 框架加入 RSI(14) bullish hook divergence 過濾。
跨資產驗證 SIVR-015 divergence pattern 泛化性。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_009_rsi_divergence_mr.config import (
    COPX009Config,
    create_default_config,
)
from trading.experiments.copx_009_rsi_divergence_mr.signal_detector import (
    COPX009SignalDetector,
)


class COPX009Strategy(ExecutionModelStrategy):
    """COPX-009：RSI bullish divergence + pullback+WR+ATR 均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX009Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            if config.enable_atr_filter:
                print(
                    f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                    f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
                )
            else:
                print("  ATR 波動率過濾: 已停用 (disabled)")
            print(
                f"  RSI({config.rsi_period}) Bullish Hook: "
                f"lookback {config.rsi_hook_lookback} 日 / delta >= {config.rsi_hook_delta} / "
                f"near-low RSI <= {config.rsi_hook_max_min}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
