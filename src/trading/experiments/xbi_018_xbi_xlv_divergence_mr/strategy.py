"""XBI-018: XBI-XLV Cross-Asset Divergence Filter on VIX Bands MR 策略

XBI-017 Att1 框架（lesson #22 vol stability + lesson #24 VIX BANDS）+
**XBI-XLV cross-asset divergence cap**（lesson #20 v3，repo 首次應用於 XBI）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_018_xbi_xlv_divergence_mr.config import (
    XBI018Config,
    create_default_config,
)
from trading.experiments.xbi_018_xbi_xlv_divergence_mr.signal_detector import (
    XBI018SignalDetector,
)


class XBI018XbiXlvDivergenceMRStrategy(ExecutionModelStrategy):
    """XBI-018：XBI-XLV Cross-Asset Divergence Filter MR 策略（含成交模型）"""

    slippage_pct: float = 0.001  # 0.1%（XBI 高流動板塊 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI018SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI018Config):
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
            rs_components = []
            if config.use_rs_short:
                rs_components.append(
                    f"{config.rs_lookback_short}d <= {config.max_rs_excess_short:+.1%}"
                )
            if config.use_rs_long:
                rs_components.append(
                    f"{config.rs_lookback_long}d <= {config.max_rs_excess_long:+.1%}"
                )
            if rs_components:
                print(f"  XBI-{config.xlv_ticker} RS cap: " + " AND ".join(rs_components))
            else:
                print("  XBI-XLV RS cap: 已停用")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
