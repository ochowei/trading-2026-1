"""
IBIT-007: Keltner 通道下軌 + 回檔 + 反轉 K 線均值回歸策略
(IBIT Keltner Lower Band + Pullback + Reversal Bar Mean Reversion)

進場使用波動率自適應 Keltner 下軌 + 回檔深度 + 日內反轉三重確認，
出場使用固定對稱 TP/SL（TP +4.5%/SL -4.0%）。成交模型採隔日開盤市價。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ibit_007_keltner_lower_mr.config import (
    IBIT007Config,
    create_default_config,
)
from trading.experiments.ibit_007_keltner_lower_mr.signal_detector import (
    IBIT007SignalDetector,
)


class IBIT007Strategy(ExecutionModelStrategy):
    """IBIT-007：Keltner 通道下軌 + 回檔 + 反轉 K 線均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 加密貨幣 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IBIT007SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IBIT007Config):
            print(
                f"  Keltner 下軌: EMA({config.ema_period}) - "
                f"{config.keltner_multiplier} × ATR({config.atr_period})"
            )
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print("  日內反轉: Close > Open")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
