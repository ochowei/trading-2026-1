"""
COPX-001: 回檔 + Williams %R 均值回歸配置
(COPX Pullback + Williams %R Mean Reversion Config)

COPX (Global X Copper Miners ETF) 日波動度 ~2.25%，與 GLD 比率 1.87x。
參考 XBI-001 / SIVR-005 回檔範圍 + Williams %R 架構，按 COPX 波動度縮放參數：
- 回檔範圍：9-18%（過濾淺回檔與極端崩盤）
- WR(10) ≤ -80（標準超賣門檻）
- TP +3.5%（銅礦 ETF 均值回歸幅度）
- SL -5.0%（非對稱寬停損）
- 不使用追蹤停損（日波動 2.25% 禁用區域）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPXPullbackWRConfig(ExperimentConfig):
    """COPX 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.09  # 回檔 ≥ 9%
    pullback_upper: float = -0.18  # 回檔上限 18%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> COPXPullbackWRConfig:
    return COPXPullbackWRConfig(
        name="copx_001_pullback_wr",
        experiment_id="COPX-001",
        display_name="COPX Pullback + Williams %R Mean Reversion",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.050,  # -5.0%（非對稱寬停損）
        holding_days=15,  # 15 天
    )
