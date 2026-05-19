"""CIBR-017: ^VIX Implied-Vol Regime BANDS Filter MR 策略

CIBR-008 Att2 框架（BB 下軌 + 回檔上限混合進場）+ ^VIX BANDS 過濾。
Repo 第 2 次 lesson #24 family BANDS 變體跨資產驗證（XBI-017 後首次），
首次於網路安全板塊 ETF（CIBR）。含成交模型（隔日開盤市價進場）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_017_vix_bands_mr.config import (
    CIBR017Config,
    create_default_config,
)
from trading.experiments.cibr_017_vix_bands_mr.signal_detector import (
    CIBR017VixBandsMRDetector,
)


class CIBR017VixBandsMRStrategy(ExecutionModelStrategy):
    """CIBR-017：^VIX BANDS Filter MR 策略（含成交模型）"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR017VixBandsMRDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR017Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" <= {abs(config.pullback_cap):.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR FLOOR: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            if config.use_vix_bands:
                print(
                    f"  ^VIX BANDS gate: {config.vix_ticker} <= {config.vix_low_threshold:.1f}"
                    f" OR > {config.vix_high_threshold:.1f}"
                )
            else:
                print("  ^VIX BANDS gate: 已停用")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
