"""
URA-010：Williams Vix Fix 資本化 + 回檔深度均值回歸策略
(URA Williams Vix Fix Capitulation + Pullback Depth Mean Reversion)

進場使用 WVF 上穿 BB 上軌（capitulation depth detection）+ 10日回檔深度
雙重確認，出場沿用 URA-004 對稱範圍（TP +6.0%/SL -5.5%/20天）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_010_wvf_capitulation_mr.config import (
    URA010Config,
    create_default_config,
)
from trading.experiments.ura_010_wvf_capitulation_mr.signal_detector import (
    URA010SignalDetector,
)


class URA010WVFCapitulationStrategy(ExecutionModelStrategy):
    """URA-010：Williams Vix Fix 資本化 + 回檔深度均值回歸"""

    slippage_pct: float = 0.001  # 0.10%（沿用 URA 系列）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URA010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URA010Config):
            print(
                f"  WVF({config.wvf_lookback}) > BB_upper("
                f"{config.wvf_bb_lookback}, {config.wvf_bb_stddev:.1f}σ)"
                "  ← capitulation 深度極值"
            )
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
