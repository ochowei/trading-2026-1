"""XBI-020: ^VIX Implied-Vol DIRECTION Regime Gate Pullback MR 策略

XBI-017 Att1 框架（lesson #22 vol stability gate + lesson #24 VIX BANDS）
+ ^VIX DIRECTION (lookback-day change) CEILING。
Repo 首次 lesson #24 family DIRECTION 變體應用於 XBI（XBI-017 為 BANDS 變體）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_020_vix_direction_mr.config import (
    XBI020Config,
    create_default_config,
)
from trading.experiments.xbi_020_vix_direction_mr.signal_detector import (
    XBI020VixDirectionMRDetector,
)


class XBI020VixDirectionMRStrategy(ExecutionModelStrategy):
    """XBI-020：^VIX DIRECTION CEILING Filter MR 策略（含成交模型）"""

    slippage_pct: float = 0.001  # 0.1%（XBI 高流動板塊 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI020VixDirectionMRDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI020Config):
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
            if config.use_vix_bands:
                print(
                    f"  ^VIX BANDS gate: {config.vix_ticker} <= {config.vix_low_threshold:.1f}"
                    f" OR > {config.vix_high_threshold:.1f}"
                )
            else:
                print("  ^VIX BANDS gate: 已停用")
            if config.use_vix_direction:
                print(
                    f"  ^VIX DIRECTION CEILING: {config.vix_ticker}"
                    f" {config.vix_direction_lookback}d change ≤"
                    f" {config.max_vix_change:+.1f}"
                )
            else:
                print("  ^VIX DIRECTION CEILING: 已停用")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
