"""
GLD-009: BB Squeeze Breakout 配置
GLD BB Squeeze Breakout Configuration

首次在 GLD 上嘗試突破策略。GLD 為單一商品 ETF（持有金條），
不受板塊 ETF 分散化稀釋突破動能的問題（lesson #71）。
黃金歷史上有明確的盤整→突破模式（如 2018-2019 → 2020 突破）。

三次嘗試記錄：
- Att1: TP+3.0%/SL-3.0%/20d（無追蹤停損）
  → Part A Sharpe 0.28 / Part B 0.27（A/B 平衡優秀但 Sharpe 不足，未超越 GLD-008）
- Att2: TP+3.0%/SL-3.5%/20d
  → Part A Sharpe 0.20 / Part B 0.19（SL 放寬無效，同批訊號停損更大）
- Att3: TP+4.0%/SL-3.0%/20d + 追蹤停損（+2.0% 啟動，1.0% 距離）
  → Part A Sharpe 0.17 / Part B 0.14（追蹤停損距離 1.0% ≈ 日波動 1.1%，正常回檔觸發出場）

結論：GLD 日波動 1.1% 限制突破幅度，WR 65% × +3.0%/-3.0% 盈虧比僅 ~1:1。
突破策略在 GLD 上不如均值回歸（GLD-008 Sharpe 0.45/2.33）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD009Config(ExperimentConfig):
    """GLD BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 7


def create_default_config() -> GLD009Config:
    """建立預設配置"""
    return GLD009Config(
        name="gld_009_bb_squeeze_breakout",
        experiment_id="GLD-009",
        display_name="GLD BB Squeeze Breakout",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.03,
        holding_days=20,
    )
