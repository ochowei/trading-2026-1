"""
TQQQ 恐慌抄底策略配置 (TQQQ Capitulation Buy Strategy Configuration)
定義 TQQQ 專屬策略的所有參數與閾值。
Defines all parameters and thresholds for the TQQQ capitulation buy strategy.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQConfig(ExperimentConfig):
    """TQQQ 恐慌抄底策略配置"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20        # 回撤計算的高點回望天數
    drawdown_threshold: float = -0.15  # 從 20 日高點回撤 ≥ 15%
    rsi_period: int = 5                # 短週期 RSI 捕捉急性恐慌
    rsi_threshold: float = 25.0        # RSI(5) < 25 極端超賣
    volume_multiplier: float = 1.5     # 成交量 > 1.5 倍均量
    volume_sma_period: int = 20        # 均量計算週期

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 3             # 同一波跌勢中僅取第一個訊號


def create_default_config() -> TQQQConfig:
    """建立預設 TQQQ 配置 (Create default TQQQ config)"""
    return TQQQConfig(
        name="tqqq_capitulation",
        display_name="TQQQ 恐慌抄底策略 — Capitulation Buy Strategy",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,
        stop_loss=-0.08,
        holding_days=7,
    )
