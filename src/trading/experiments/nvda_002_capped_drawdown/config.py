"""
NVDA 寬停損均值回歸策略配置
NVDA Wide Stop-Loss Mean Reversion Configuration

基於 NVDA-001，嘗試寬停損 (-12%) + 長持倉 (25d)。
結論：未能超越 NVDA-001，詳見 EXPERIMENTS_NVDA.md。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDACappedDrawdownConfig(ExperimentConfig):
    """NVDA 寬停損策略專屬參數"""

    # RSI(2) 條件
    rsi_period: int = 2
    rsi_threshold: float = 5.0  # RSI(2) < 5（極端超賣）

    # 2日急跌條件
    drop_2d_threshold: float = -0.07  # 2日累計跌幅 >= 7%

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> NVDACappedDrawdownConfig:
    """建立預設配置"""
    return NVDACappedDrawdownConfig(
        name="nvda_002_capped_drawdown",
        experiment_id="NVDA-002",
        display_name="NVDA Wide SL + RSI(2) Mean Reversion",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,  # +8% 獲利目標（同 NVDA-001）
        stop_loss=-0.12,  # -12% 停損（比 NVDA-001 -10% 更寬）
        holding_days=25,  # 25 天持倉（比 NVDA-001 15天更長）
    )
