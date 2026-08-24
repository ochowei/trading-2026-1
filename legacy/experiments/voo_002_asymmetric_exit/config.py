"""
VOO-002: RSI(2) 非對稱出場均值回歸
(VOO RSI(2) Asymmetric Exit Mean Reversion)

基於 VOO-001 相同進場條件，套用 DIA-003 的非對稱出場策略：
- 寬停損 SL -3.5%（挽回暫時深跌後反彈的交易）
- 延長持倉至 20 天（給予更多時間達標）

Based on VOO-001 entry conditions, applying DIA-003's asymmetric exit:
- Wider SL -3.5% (rescues trades that temporarily dip below -2.5%)
- Extended holding to 20 days (more time to reach TP)
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VOOAsymmetricConfig(ExperimentConfig):
    """VOO RSI(2) 非對稱出場參數"""

    # RSI(2) 參數（同 VOO-001）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10（極端超賣）

    # 2 日累計跌幅過濾（同 VOO-001）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 VOO-001）
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) >= 40%

    # 冷卻期（同 VOO-001）
    cooldown_days: int = 5


def create_default_config() -> VOOAsymmetricConfig:
    return VOOAsymmetricConfig(
        name="voo_002_asymmetric_exit",
        experiment_id="VOO-002",
        display_name="VOO RSI(2) Asymmetric Exit Mean Reversion",
        tickers=["VOO"],
        data_start="2010-10-01",
        profit_target=0.025,  # +2.5%（同 VOO-001）
        stop_loss=-0.030,  # -3.0%（非對稱寬停損）
        holding_days=20,  # 20 天（延長持倉）
    )
