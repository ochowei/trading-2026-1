"""
EEM-007: Trend Momentum Pullback → Regime-Filtered Mean Reversion
(EEM 趨勢動量回調 → 牛市政權過濾均值回歸)

EEM 前 6 個實驗探索了均值回歸、BB Squeeze 突破、RS 動量。
本實驗先嘗試趨勢動量回調（Att1-2），發現市場狀態依賴過強後，
Att3 轉向牛市政權過濾均值回歸：在 SMA(200) 牛市中做 RSI(2) 均值回歸。

Att1: SMA(50) + 20d ROC > 2% + 10d drawdown >= 2% + cooldown 10
      TP +3.0% / SL -3.0% / 15天
  → Part A 0.19 (28訊號, WR 60.7%), Part B -0.32 (10訊號, WR 30.0%)
  問題：ROC 2% 門檻過鬆，弱上升趨勢中回調不反彈

Att2: ROC > 3% + WR(10) < -60 超賣確認 + 10d drawdown >= 2%
      TP +3.0% / SL -3.0% / 15天
  → Part A 0.43 (15訊號, WR 66.7%), Part B -0.37 (6訊號, WR 33.3%)
  問題：市場狀態依賴 — Part A 有強趨勢 Part B 為震盪市

Att3: 策略轉向 — 牛市政權過濾均值回歸
      SMA(200) 牛市 + RSI(2)<10 + 2d decline>=1.5% + ClosePos>=40%
      + ATR(5)/ATR(20)>1.15 + cooldown 10
      TP +3.0% / SL -3.0% / 20天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM007Config(ExperimentConfig):
    """EEM-007 牛市政權過濾均值回歸參數"""

    # 牛市政權過濾
    regime_sma_period: int = 200  # SMA(200) 長期趨勢

    # RSI 超賣
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 急跌確認
    decline_days: int = 2
    decline_threshold: float = 0.015  # 2日跌幅 >= 1.5%

    # 日內反轉
    close_pos_threshold: float = 0.40  # ClosePos >= 40%

    # 波動率飆升
    atr_short: int = 5
    atr_long: int = 20
    atr_ratio_threshold: float = 1.15  # ATR(5)/ATR(20) > 1.15

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EEM007Config:
    return EEM007Config(
        name="eem_007_trend_momentum_pullback",
        experiment_id="EEM-007",
        display_name="EEM Regime-Filtered Mean Reversion",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
