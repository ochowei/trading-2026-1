"""
CIBR 回檔 + Williams %R 均值回歸配置 (CIBR Pullback + Williams %R Mean Reversion Config)

參考 SIVR-003 架構，以「10 日高點回檔幅度」搭配 Williams %R 確認超賣。
CIBR（網路安全 ETF）日波動約 1.53%，為 GLD 的 1.37 倍，屬低中波動板塊 ETF。
參數由 GLD-007 / SIVR-003 按波動度比例內插：
- 回檔門檻：5%（GLD 3%、SIVR 7% 之間內插）
- 止盈/停損：+3.5% / -4.0%（與 GLD-007 相近，CIBR 波動適中）
- 不使用追蹤停損（日波動 1.53% 在追蹤停損有效邊界外）

Adapts SIVR-003's pullback + Williams %R approach for CIBR with volatility-scaled params.
No trailing stop (daily vol 1.53% is at the boundary where trailing stop becomes unreliable).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBRPullbackWRConfig(ExperimentConfig):
    """CIBR 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # 回檔 >=5%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80 (超賣)
    cooldown_days: int = 8


def create_default_config() -> CIBRPullbackWRConfig:
    return CIBRPullbackWRConfig(
        name="cibr_001_pullback_wr",
        experiment_id="CIBR-001",
        display_name="CIBR Pullback + Williams %R Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=18,  # 18 天
    )
