"""
EEM-018: ^VIX BANDS Regime Gate on Vol-Transition MR Strategy

延伸 EEM-014 Att2 框架，新增 ^VIX BANDS regime gate（U-shape regime hypothesis
跨資產移植自 XBI-017 Att1）。出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_018_vix_bands_mr.config import (
    EEM018Config,
    create_default_config,
)
from trading.experiments.eem_018_vix_bands_mr.signal_detector import (
    EEM018VixBandsMRDetector,
)


class EEM018Strategy(ExecutionModelStrategy):
    """EEM-018: ^VIX BANDS Regime Gate on Vol-Transition MR"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM018VixBandsMRDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM018Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日報酬下限: <= {config.twoday_return_floor:.2%}（同 EEM-014 Att2 甜蜜點）")
            print(
                f"  ^VIX BANDS gate: VIX <= {config.vix_low_threshold:.1f}"
                f" OR VIX > {config.vix_high_threshold:.1f}"
                f"（排除中等 VIX 帶 [{config.vix_low_threshold:.1f},"
                f" {config.vix_high_threshold:.1f}]，repo 第 2 次 BANDS 變體）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
