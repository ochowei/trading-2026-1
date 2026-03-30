"""
XBI-001: 回檔 + Williams %R 均值回歸配置
(XBI Pullback + Williams %R Mean Reversion Config)

XBI (SPDR S&P Biotech ETF) 日波動度 ~2.0%，與 GLD 比率 1.81x。
參考 SIVR-005 回檔範圍 + Williams %R 架構，按 XBI 波動度縮放參數：
- 回檔範圍：8-20%（過濾淺回檔與極端崩盤）
- WR(10) ≤ -80（標準超賣門檻）
- TP +3.5%（均值回歸幅度）
- SL -5.0%（非對稱寬停損，生技板塊需要呼吸空間）
- 不使用追蹤停損（日波動 2% 邊界區域，預設不用）

Adapts SIVR-005's pullback range + Williams %R approach for XBI with vol-scaled params.
No trailing stop (daily vol ~2% is at the boundary, default to no trailing).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBIPullbackWRConfig(ExperimentConfig):
    """XBI 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 ≥ 8%
    pullback_upper: float = -0.20  # 回檔上限 20%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> XBIPullbackWRConfig:
    return XBIPullbackWRConfig(
        name="xbi_001_pullback_wr",
        experiment_id="XBI-001",
        display_name="XBI Pullback + Williams %R Mean Reversion",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.050,  # -5.0%（非對稱寬停損）
        holding_days=15,  # 15 天
    )
