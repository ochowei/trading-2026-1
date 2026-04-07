"""
TSLA-010: RSI(5) Mean Reversion 配置
TSLA RSI(5) Mean Reversion Configuration

改編 SOXL-006 框架至 TSLA：RSI(5) 取代 RSI(2)（高波動資產更穩定）。
Att1: 20日回看 DD[-30%,-15%] RSI(5)<20 2日≤-6% SL-10% → Part A -0.23/Part B 0.20
Att2: 收緊 RSI(5)<15 + 2日≤-8% + SL-12% → Part A -0.24/Part B 0.00 (3訊號100%WR)
Att3: 60日回看 DD[-30%,-20%] + RSI(5)<15 + 2日≤-8% + SL-12% + 25天 + cd15
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLARSI5MeanRevConfig(ExperimentConfig):
    """TSLA RSI(5) Mean Reversion 策略專屬參數"""

    # 回撤條件：收盤價低於 N 日高點的幅度
    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.20  # -20% 下限
    drawdown_cap: float = -0.30  # -30% 上限（過濾極端崩盤）

    # RSI(5) 超賣
    rsi_period: int = 5
    rsi_threshold: float = 15.0  # RSI(5) < 15

    # 2日急跌幅度
    drop_2d_threshold: float = -0.08  # 2日跌幅 ≤ -8%

    # 冷卻期
    cooldown_days: int = 15

    # 成交模型滑價
    slippage_pct: float = 0.0015  # 0.15% 個股滑價


def create_default_config() -> TSLARSI5MeanRevConfig:
    """建立預設 TSLA-010 配置"""
    return TSLARSI5MeanRevConfig(
        name="tsla_010_rsi5_mean_reversion",
        experiment_id="TSLA-010",
        display_name="TSLA RSI(5) Mean Reversion (SOXL-006 Framework)",
        tickers=["TSLA"],
        data_start="2018-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.10,  # +10%
        stop_loss=-0.12,  # -12%
        holding_days=25,  # 25 天（延長持倉）
    )
