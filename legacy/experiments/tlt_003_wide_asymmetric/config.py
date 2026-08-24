"""
TLT 寬停損非對稱出場均值回歸配置
(TLT Wide Asymmetric Exit Mean Reversion Config)

基於 TLT-001/002 進場架構，改用寬停損非對稱出場：
- SL -4.0%（原 -3.5%）：給予利率波動更多呼吸空間，挽回邊際深跌交易
- 冷卻期 10 天（原 7 天）：減少 2022 升息期連續進場
- 移除 60 日跌幅過濾（TLT-002 驗證僅邊際改善）

迭代紀錄：
- Att1: TP+3.0%/SL-5.0%/cd10 → Part A Sharpe -0.27（更差），Part B 0.33
- Att2: TP+3.0%/SL-3.5%/cd15 → Part A Sharpe -0.33（最差），Part B 0.41
- Att3: TP+2.5%/SL-4.0%/cd10 → Part A Sharpe -0.20（持平），Part B 0.46（最佳版本）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLTWideAsymmetricConfig(ExperimentConfig):
    """TLT 寬停損非對稱出場參數"""

    # 回檔範圍進場（同 TLT-001/002）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-001/002）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-001/002）
    close_position_threshold: float = 0.4

    # 冷卻期（加長：7 → 10 天）
    cooldown_days: int = 10


def create_default_config() -> TLTWideAsymmetricConfig:
    return TLTWideAsymmetricConfig(
        name="tlt_003_wide_asymmetric",
        experiment_id="TLT-003",
        display_name="TLT Wide Asymmetric Exit Mean Reversion",
        tickers=["TLT"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（同 TLT-002）
        stop_loss=-0.04,  # -4.0%（原 -3.5%，試中間值）
        holding_days=20,  # 20 天（同前）
    )
