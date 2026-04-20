"""
IBIT-008: 單日 Range Expansion Climax + 強日內反轉均值回歸策略
(IBIT Range Expansion Climax Mean Reversion)

進場使用 TR/ATR(20) ≥ 2.0 爆發性 climax + ClosePos ≥ 50% 強日內反轉 +
10 日回檔 -6% ~ -20% 下跌 regime 過濾 + WR(10) ≤ -70 超賣確認五重條件，
出場使用固定對稱 TP/SL（TP +4.5%/SL -4.0%）。成交模型採隔日開盤市價。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ibit_008_range_expansion_mr.config import (
    IBIT008Config,
    create_default_config,
)
from trading.experiments.ibit_008_range_expansion_mr.signal_detector import (
    IBIT008SignalDetector,
)


class IBIT008Strategy(ExecutionModelStrategy):
    """IBIT-008：單日 Range Expansion Climax + 強日內反轉均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 加密貨幣 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IBIT008SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IBIT008Config):
            print(
                f"  Range Expansion: TR / ATR({config.atr_period}) >= "
                f"{config.tr_ratio_threshold}"
            )
            print(f"  Close Position: ClosePos >= {config.close_pos_threshold:.0%}")
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
