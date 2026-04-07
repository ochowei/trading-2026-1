"""
TQQQ-015: QQQ Momentum → Trade TQQQ 配置
QQQ Momentum Configuration (trade TQQQ for 3x amplification)

Att3: 改用動量策略。QQQ 10日 ROC > 5% + SMA(50) + SMA(200) 確認牛市動量。
在 QQQ 上偵測強勁動量訊號，然後交易 TQQQ 獲得 3 倍放大報酬。
這是 TQQQ 首次嘗試動量策略（前 14 個實驗均為均值回歸/恐慌抄底）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQQqqBreakoutConfig(ExperimentConfig):
    """TQQQ-015 QQQ Momentum 策略專屬參數"""

    # QQQ data ticker
    qqq_ticker: str = "QQQ"

    # Momentum parameters (applied to QQQ)
    momentum_threshold: float = 5.0  # QQQ 10-day ROC > 5%

    # Cooldown
    cooldown_days: int = 20

    # Execution model
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQQqqBreakoutConfig:
    """建立預設配置"""
    return TQQQQqqBreakoutConfig(
        name="tqqq_015_qqq_trend_breakout",
        experiment_id="TQQQ-015",
        display_name="TQQQ QQQ Momentum — QQQ ROC(10)>5% → Trade TQQQ",
        tickers=["TQQQ"],
        data_start="2018-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.10,
        stop_loss=-0.10,
        holding_days=15,
    )
