"""
URA-006: 相對強度回調買入
(URA Relative Strength Pullback Entry)

策略邏輯：URA 相對 XLE（能源板塊）有超額表現時，
代表鈾礦有板塊特有的催化劑（政策、供應），買入回調。

Att1: SMA(20)>SMA(50) 金叉 + 回調 3-8% + TP+6%/SL-5.5%/20d
  → Part A 0.23 / Part B 0.03（SMA 交叉在 2.34% 日波動下太敏感，Part B 隨機）
Att2: ROC(20)>10% 動量 + SMA(50) + 回調 3-8% + TP+7%/SL-7%/25d/cd15
  → Part A -0.21 / Part B -0.10（動量門檻過濾後 WR 40-45%，策略虧損）
Att3: URA vs XLE 相對強度 + SMA(50) + 回調 3-8% + TP+6%/SL-6%/20d/cd15
  → 參考 TSM-008 成功模式，用板塊相對強度作為進場訊號
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URATrendPullbackConfig(ExperimentConfig):
    """URA 相對強度回調策略專屬參數"""

    # 相對強度
    reference_ticker: str = "XLE"
    relative_strength_period: int = 20
    relative_strength_min: float = 0.08  # URA 20日報酬 - XLE 20日報酬 >= 8%

    # 趨勢位置
    sma_trend_period: int = 50

    # 回調進場
    pullback_lookback: int = 5  # 5日高點回看
    pullback_min: float = 0.03  # 最少回調 3%
    pullback_max: float = 0.08  # 最多回調 8%

    cooldown_days: int = 15


def create_default_config() -> URATrendPullbackConfig:
    return URATrendPullbackConfig(
        name="ura_006_trend_pullback",
        experiment_id="URA-006",
        display_name="URA RS Pullback (vs XLE)",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.06,  # +6.0%
        stop_loss=-0.06,  # -6.0%
        holding_days=20,
    )
