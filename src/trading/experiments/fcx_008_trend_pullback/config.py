"""
FCX-008: 2日急跌 + 極端超賣均值回歸配置
FCX Sharp Drop + Extreme Oversold Mean Reversion Configuration

Att1: 趨勢跟蹤 — FAILED (Part A -0.00, Part B -0.63)
Att2: FCX-001 + ATR > 1.05 — Part B 改善但 Part A 嚴重退化 (min 0.25)
Att3: FCX-001 + 2日急跌 <= -5%
  假說：USO-013 的 2日急跌過濾在 USO 上極為成功（Sharpe 0.26/0.82），
  比 ATR 更直接偵測恐慌拋售。FCX 日波動 2-4%，-5% 門檻約 0.8-1.3σ/日。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX008Config(ExperimentConfig):
    """FCX-008 2日急���極端超賣策略參數"""

    # 進場指標（同 FCX-001）
    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.18  # 低於 60 日高點 18%
    rsi_period: int = 10
    rsi_threshold: float = 28.0  # RSI(10) < 28
    sma_period: int = 50
    sma_deviation_threshold: float = -0.08  # SMA(50) 乖離 <= -8%
    cooldown_days: int = 15

    # 2日急跌過濾器（新增，來自 USO-013 框架）
    two_day_drop_threshold: float = -0.05  # 2日跌幅 <= -5%


def create_default_config() -> FCX008Config:
    return FCX008Config(
        name="fcx_008_trend_pullback",
        experiment_id="FCX-008",
        display_name="FCX Sharp Drop + Extreme Oversold",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.10,  # +10%（同 FCX-001）
        stop_loss=-0.12,  # -12%（同 FCX-001，lesson #37 底線）
        holding_days=25,  # 25 天（同 FCX-001）
    )
