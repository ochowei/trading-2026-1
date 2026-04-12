"""
EWZ-001: 回檔 + Williams %R 均值回歸
(EWZ Pullback + Williams %R Mean Reversion)

參考 SIVR-003 成功經驗，以「10 日高點回檔幅度」搭配 Williams %R ��認超賣。
EWZ 日波動 ~1.75%（GLD 的 1.56 倍），參數依波動度縮放：
- 回檔��檻：7%（與 SIVR-003 相同，篩選較深回調避免淺回調假訊號）
- 止盈/停損：+4.0% / -4.0%（風報��� 1:1，寬 SL 避免日內波動觸發停損）
- 持倉 15 天（較高波動 = 更快回歸）
- 不使用追蹤停損（日波動 > 1.5%，cross-asset lesson #2 禁用）

Adapts SIVR-003's pullback + Williams %R approach for EWZ with volatility-scaled params.
No trailing stop (daily vol 1.75% exceeds 1.5% threshold per cross-asset lesson #2).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZPullbackWRConfig(ExperimentConfig):
    """EWZ 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> EWZPullbackWRConfig:
    return EWZPullbackWRConfig(
        name="ewz_001_pullback_wr",
        experiment_id="EWZ-001",
        display_name="EWZ Pullback + Williams %R Mean Reversion",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.040,  # +4.0%
        stop_loss=-0.040,  # -4.0%
        holding_days=15,
    )
