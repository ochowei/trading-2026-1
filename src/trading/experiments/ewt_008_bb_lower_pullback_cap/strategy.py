"""
EWT-008: BB Lower Band + Pullback Cap Hybrid Mean Reversion Strategy

延伸 EWJ-003 / VGK-007 / CIBR-008 / EWZ-006 的混合進場架構至 EWT。
使用 BB(20, 2.0) 下軌觸及 + 10日高點回檔上限 8% 作為混合進場訊號。
搭配 WR + ClosePos + ATR 三重品質過濾。
出場使用 EWT 驗證甜蜜點（TP+3.5%/SL-4%/20d），成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_008_bb_lower_pullback_cap.config import (
    EWT008Config,
    create_default_config,
)
from trading.experiments.ewt_008_bb_lower_pullback_cap.signal_detector import (
    EWT008SignalDetector,
)


class EWT008Strategy(ExecutionModelStrategy):
    """EWT BB Lower + Pullback Cap Hybrid MR (EWT-008)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT008SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT008Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= -{abs(config.pullback_cap):.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
