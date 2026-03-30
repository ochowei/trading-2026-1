"""
IWM-002: 回檔 + Williams %R 均值回歸配置
(IWM Pullback + Williams %R Mean Reversion Config)

IWM (Russell 2000 ETF) 日波動度 ~1.5-2%，介於 SPY (~1.2%) 和 XBI (~2.0%) 之間。
參考 XBI-001 / COPX-001 回檔範圍 + Williams %R 架構，按 IWM 波動度縮放：
- 回檔範圍：6-15%（IWM 回調幅度較 XBI 淺，下限 6%；上限 15% 過濾極端崩盤）
- WR(10) ≤ -80（標準超賣門檻）
- TP +3.5%（高於 IWM-001 +3.0%，利用回檔深度捕捉更大反彈）
- SL -4.5%（維持 IWM-001 已驗證的寬停損）
- 持倉 20 天（維持 IWM-001 充分回歸時間）
- 不使用追蹤停損（日波動 ~1.5-2%，邊界區域不用）

三次嘗試均未能在風險調整後報酬上超越 IWM-001：
- Att1: Pullback 6-15%, TP+3.5%/SL-4.5% → Part A Sharpe 0.02, Part B Sharpe 0.25
- Att2: Pullback 8-15% + ClosePos≥40%, TP+3.5%/SL-4.5% → Part A 0.07, Part B 0.21
- Att3: Pullback 7-15%, TP+3.5%/SL-5.0% → Part A -0.02, Part B 0.11
保留 Att1 參數作為參考（Part B 最佳）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWMPullbackWRConfig(ExperimentConfig):
    """IWM 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.06  # 回檔 ≥ 6%
    pullback_upper: float = -0.15  # 回檔上限 15%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> IWMPullbackWRConfig:
    return IWMPullbackWRConfig(
        name="iwm_002_pullback_wr",
        experiment_id="IWM-002",
        display_name="IWM Pullback + Williams %R Mean Reversion",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.045,  # -4.5%（維持 IWM-001 已驗證的寬停損）
        holding_days=20,  # 20 天
    )
