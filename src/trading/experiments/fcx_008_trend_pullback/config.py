"""
FCX-008: 波動率自適應極端超賣均值回歸配置
FCX Volatility-Adaptive Extreme Oversold Mean Reversion Configuration

Att1: 趨勢跟蹤 — FAILED (Part A -0.00, Part B -0.63)
Att2: FCX-001 進場架構 + ATR(5)/ATR(20) > 1.05 波動率過濾
  假說：COPX-007 的 ATR 過濾在 COPX（日波動 2.25%）上成功（+28.6%），
  移植至 FCX（日波動 2-4%），預期過濾掉慢磨下跌型假訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX008Config(ExperimentConfig):
    """FCX-008 波動率自適應極端超賣策略參數"""

    # 進場指標（同 FCX-001）
    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.18  # 低於 60 日高點 18%
    rsi_period: int = 10
    rsi_threshold: float = 28.0  # RSI(10) < 28
    sma_period: int = 50
    sma_deviation_threshold: float = -0.08  # SMA(50) 乖離 <= -8%
    cooldown_days: int = 15

    # 波動率自適應過濾器（新增，來自 COPX-007）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05  # ATR(5)/ATR(20) > 1.05


def create_default_config() -> FCX008Config:
    return FCX008Config(
        name="fcx_008_trend_pullback",
        experiment_id="FCX-008",
        display_name="FCX Volatility-Adaptive Extreme Oversold",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.10,  # +10%（同 FCX-001）
        stop_loss=-0.12,  # -12%（同 FCX-001，lesson #37 底線）
        holding_days=25,  # 25 天（同 FCX-001）
    )
