"""
FXI-001: 回檔 + Williams %R 均值回歸配置
(FXI Pullback + Williams %R Mean Reversion Config)

參考 SIVR-003 成功經驗，以「10 日高點回檔幅度」搭配 Williams %R 確認超賣。
FXI 日波動 ~2.0%（GLD 的 1.78 倍），與 SIVR 波動度相近，使用相同參數架構：
- 回檔門檻：7%（與 SIVR-003 一致）
- 止盈/停損：+3.5% / -3.5%（風報比 1:1，利用勝率 > 60% 獲利）
- 不使用追蹤停損（日波動 ~2% 禁用追蹤停損）

Adapts SIVR-003's pullback + Williams %R approach for FXI with similar volatility.
No trailing stop (daily vol ~2% makes trailing stop ineffective).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXIPullbackWRConfig(ExperimentConfig):
    """FXI 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> FXIPullbackWRConfig:
    return FXIPullbackWRConfig(
        name="fxi_001_pullback_wr",
        experiment_id="FXI-001",
        display_name="FXI Pullback + Williams %R Mean Reversion",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,  # 15 天
    )
