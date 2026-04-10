"""
URA-007: 波動率自適應均值回歸配置
(URA Volatility-Adaptive Mean Reversion Config)

Att1: URA-004 + ATR > 1.05 → Part A 0.27/Part B 0.71, min 0.27（ATR移除5贏1輸）
Att2: RSI(2) + ATR > 1.1（無2日跌幅）→ Part A 0.07/Part B 1.19, min 0.07（更差）
Att3: URA-004 + WR(10) ≤ -80 雙振盪器確認，鎖定 RSI(2) 與 WR(10) 同時極端超賣
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA007Config(ExperimentConfig):
    """URA-007 波動率自適應均值回歸參數"""

    # 進場指標（URA-004 基礎 + WR(10) 確認）
    pullback_lookback: int = 10  # 10日回看
    pullback_threshold: float = -0.10  # 回檔 >= 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    two_day_decline: float = -0.03  # 2日跌幅 ≤ -3%
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) ≤ -80（雙振盪器確認）
    cooldown_days: int = 10


def create_default_config() -> URA007Config:
    return URA007Config(
        name="ura_007_vol_adaptive",
        experiment_id="URA-007",
        display_name="URA Volatility-Adaptive Mean Reversion",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,  # +6.0%（同 URA-004）
        stop_loss=-0.055,  # -5.5%（同 URA-004）
        holding_days=20,  # 20 天（同 URA-004）
    )
