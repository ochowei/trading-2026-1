"""
SIVR-016: Williams Vix Fix Capitulation Mean Reversion Strategy

Repo 第 2 次 WVF 試驗（URA-010 後首次），亦為 WVF 在 SIVR 上的首次嘗試。
驗證 URA-010 的跨資產假設：WVF + 深回檔模式適用於 Part A/B 兩段皆活躍
MR regime 的高波動資產（SIVR 2.34% vol、1.5-2x GLD）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_016_wvf_capitulation_mr.config import (
    SIVR016Config,
    create_default_config,
)
from trading.experiments.sivr_016_wvf_capitulation_mr.signal_detector import (
    SIVR016SignalDetector,
)


class SIVR016Strategy(ExecutionModelStrategy):
    """SIVR Williams Vix Fix Capitulation MR (SIVR-016)"""

    slippage_pct: float = 0.0015  # SIVR 標準滑價（同 SIVR-015）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVR016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVR016Config):
            print(
                f"  WVF 主訊號: WVF({config.wvf_lookback}) > BB_upper("
                f"{config.wvf_bb_lookback}, {config.wvf_bb_stddev}σ)"
            )
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback}日高點回檔 "
                f"{abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            if config.rsi_hook_enabled:
                print(
                    f"  RSI({config.rsi_period}) Bullish Hook: "
                    f"lookback {config.rsi_hook_lookback} 日 / "
                    f"delta ≥ {config.rsi_hook_delta} / "
                    f"near-low RSI ≤ {config.rsi_hook_max_min}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
