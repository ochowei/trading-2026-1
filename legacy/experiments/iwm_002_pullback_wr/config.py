"""
IWM-002: 回檔 + Williams %R 均值回歸
(IWM Pullback + Williams %R Mean Reversion)

IWM (Russell 2000 ETF) 日波動度 ~1.5-2%，與 GLD 比率 ~1.3-1.7x。
參考 XBI-001/COPX-001 回檔範圍 + Williams %R 架構，按 IWM 波動度縮放：
- 回檔範圍：7-18%（過濾淺回檔，7% 精選中等回檔訊號）
- WR(10) ≤ -80（標準超賣門檻）
- 收盤位置 ≥ 40%（反轉K線確認，IWM-001 驗證有效）
- TP +3.5%（利用回檔進場後更大的回歸空間）
- SL -5.0%（非對稱寬停損，匹配回檔入場的較大波動）
- 持倉 15 天（回檔回歸較快）
- 不使用追蹤停損（日波動 ~1.5-2%，邊界區域不用）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWMPullbackWRConfig(ExperimentConfig):
    """IWM 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥ 7%
    pullback_upper: float = -0.18  # 回檔上限 18%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    close_position_threshold: float = 0.4  # 反轉K線確認
    cooldown_days: int = 10


def create_default_config() -> IWMPullbackWRConfig:
    return IWMPullbackWRConfig(
        name="iwm_002_pullback_wr",
        experiment_id="IWM-002",
        display_name="IWM Pullback + Williams %R Mean Reversion",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.050,  # -5.0%（非對稱寬停損）
        holding_days=15,  # 15 天
    )
