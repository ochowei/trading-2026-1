"""
USO 回檔 + Williams %R 均值回歸配置 (USO Pullback + Williams %R Mean Reversion Config)

參考 SIVR-003 成功經驗，以「10 日高點回檔幅度」搭配 Williams %R(10) 確認超賣。
參數依 USO 波動率（日均 ~2.2%，介於 GLD 與 SIVR 之間）調整：
- 回檔門檻：6%（SIVR-003 為 7%，USO 波動略低故放寬）
- 止盈：+3.0%（低於 SIVR 的 3.5%，因原油 contango 拖累均值回歸幅度）
- 停損：-3.5%（同 SIVR-003）
- 不使用追蹤停損（日波動率 > 1.5%，追蹤停損已證實無效）
- 滑價：0.1%（USO 日均量 ~30M，流動性高）

Adapts SIVR-003's pullback + Williams %R approach for USO with volatility-scaled params.
No trailing stop (daily vol > 1.5%, proven ineffective per cross-asset lessons).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOPullbackWRConfig(ExperimentConfig):
    """USO 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.06  # 回檔 ≥6%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> USOPullbackWRConfig:
    return USOPullbackWRConfig(
        name="uso_001_pullback_wr",
        experiment_id="USO-001",
        display_name="USO Pullback + Williams %R Mean Reversion",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,  # +3.0%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,  # 15 天
    )
