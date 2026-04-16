"""
CIBR-006: Cybersecurity Sector RS Momentum Pullback 策略

在 CIBR 相對 SPY 展現超額表現時買入 CIBR 回調，
捕捉網路安全板塊相對大盤的動量效應。搭配 ATR+ClosePos 品質過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_006_rs_momentum_pullback.config import (
    CIBRRSMomentumConfig,
    create_default_config,
)
from trading.experiments.cibr_006_rs_momentum_pullback.signal_detector import (
    CIBRRSMomentumDetector,
)


class CIBRRSMomentumStrategy(ExecutionModelStrategy):
    """CIBR-006: Cybersecurity Sector RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBRRSMomentumDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBRRSMomentumConfig):
            print(
                f"  板塊 RS (Sector RS): CIBR - {config.benchmark_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            if config.use_atr_filter:
                print(
                    f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                    f" > {config.atr_ratio_threshold}"
                )
            if config.use_closepos_filter:
                print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            if config.use_sma_trend:
                print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
