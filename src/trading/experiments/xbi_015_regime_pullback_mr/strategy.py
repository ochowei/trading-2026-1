"""
XBI-015: Multi-Week Regime-Aware Pullback MR 策略

跨**策略類型**首次將 lesson #22 buffered multi-week regime gate 應用於
Pullback Mean Reversion 框架（先前 TSLA-015 / NVDA-012 / FCX-013 / COPX-011
皆於 BB Squeeze 框架，NVDA-013 於 MBPC 框架）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_015_regime_pullback_mr.config import (
    XBI015Config,
    create_default_config,
)
from trading.experiments.xbi_015_regime_pullback_mr.signal_detector import (
    XBI015RegimePullbackMRDetector,
)


class XBI015RegimePullbackMRStrategy(ExecutionModelStrategy):
    """XBI-015：Multi-Week Regime-Aware Pullback MR 策略（含成交模型）"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI015RegimePullbackMRDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI015Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(f"  反轉K線: ClosePos ≥ {config.close_position_threshold:.0%}")
            if config.use_vol_regime:
                print(
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用")
            if config.use_sma_regime:
                print(
                    f"  趨勢 regime: SMA({config.sma_regime_short})"
                    f" ≥ {config.sma_regime_ratio_min}"
                    f" × SMA({config.sma_regime_long})"
                )
            else:
                print("  趨勢 regime: 已停用")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
