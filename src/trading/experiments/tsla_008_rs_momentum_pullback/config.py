"""
TSLA-008: BB Squeeze Breakout + Golden Cross 配置
TSLA BB Squeeze with SMA Golden Cross Configuration

Att1: RS Momentum Pullback (QQQ, RS>=8%, pullback 5-10%) → Part A 0.17 / Part B -0.96
  失敗原因：TSLA vs QQQ 超額表現後回調實為動量反轉
Att2: RS Momentum Pullback (XLY, RS>=5%, pullback 3-7%) → Part A 0.06 / Part B -0.01
  失敗原因：改用板塊 ETF 和較淺回調仍無法解決 RS 框架對 TSLA 的根本問題
Att3: BB Squeeze Breakout + SMA(20)>SMA(50) Golden Cross
  假說：以 TSLA-005 已驗��的 BB Squeeze 為基礎，用 SMA 金叉取代 Close>SMA(50)
  作為更嚴格的趨勢確認，過濾 2022 熊市中 Close 暫時突破 SMA(50) 的假突破。
  這是 EXPERIMENTS_TSLA.md 明確列出的尚未嘗試方向。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA008Config(ExperimentConfig):
    """TSLA-008 BB Squeeze + Golden Cross 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_short_period: int = 20
    sma_long_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> TSLA008Config:
    return TSLA008Config(
        name="tsla_008_rs_momentum_pullback",
        experiment_id="TSLA-008",
        display_name="TSLA BB Squeeze + Golden Cross",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
