"""
COPX-012: Volatility-Acceleration-Bounded MR 策略
COPX Volatility-Acceleration-Bounded Mean Reversion Strategy

跨資產驗證 lesson #15 v2 BAND 結構在 COPX 上的有效性。
將 CIBR-014 Att2 / FXI-014 Att2 的「ATR(5)/ATR(20) ratio CEILING」過濾器
疊加於 COPX-007 的 ATR FLOOR 之上，形成 ATR ratio BAND ∈ (1.05, 1.40]。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_012_atr_ceiling_mr.config import (
    COPX012Config,
    create_default_config,
)
from trading.experiments.copx_012_atr_ceiling_mr.signal_detector import (
    COPX012SignalDetector,
)


class COPX012Strategy(ExecutionModelStrategy):
    """COPX-012：波動率加速雙向過濾均值回歸（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價（同 COPX-007）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX012Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR BAND: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) ∈"
                f" ({config.atr_ratio_floor}, {config.atr_ratio_ceiling}]"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
