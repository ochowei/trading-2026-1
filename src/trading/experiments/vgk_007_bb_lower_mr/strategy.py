"""
VGK-007: BB Lower Band Mean Reversion Strategy (Hybrid Entry)

使用 BB(20,2.0) 下軌觸及 + 10日高點回檔上限 7% 作為混合進場訊號，
搭配 WR+ClosePos+ATR 品質過濾。出場使用固定 TP/SL，成交模型採用隔日開盤市價進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_007_bb_lower_mr.config import (
    VGK007Config,
    create_default_config,
)
from trading.experiments.vgk_007_bb_lower_mr.signal_detector import (
    VGK007SignalDetector,
)


class VGK007Strategy(ExecutionModelStrategy):
    """VGK-007: BB 下軌均值回歸（混合進場）"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGK007SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGK007Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
