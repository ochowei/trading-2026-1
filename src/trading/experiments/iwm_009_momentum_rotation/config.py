"""
IWM-009: Small-Cap Momentum Pullback (IWM/SPY Relative Strength)

三次嘗試均未超越 IWM-005���min(A,B) Sharpe 0.31）：
Att1: 相對落後策略（20日/-5%/ClosePos40%/無SMA）→ Part A -0.20/Part B 0.36（Part A 7 stops，結構性弱）
Att2: 相對落後+趨勢（10日/-4%/ClosePos40%/+SMA50）→ Part A 0.10/Part B 5.19（Part B 僅 3 訊號）
Att3: 動量回檔策略（最終版本）：
  當 IWM 相對 SPY 表現強勢（正向輪動），且短期回檔時買入。
  → Part A -0.31/Part B 0.85（Part A 4/6 stops，Part B 僅 3 訊號）

結論：IWM/SPY 相對報酬在兩個方向上都無法產生穩定訊號。
- 相對落後（均值回歸）：IWM 落後常持續而非回歸
- 相對領先+回檔（動量）：2020-2021 訊號集中且品質差

進場條件：
1. IWM 20 日報酬 - SPY 20 日報酬 >= 3%（小型股正在跑贏 = 輪動中）
2. IWM 5 日報酬 <= -2%（短期回檔）
3. Close > SMA(50)（趨勢確認）
4. 冷卻期 10 個交易日

出場：TP +5.0% / SL -4.5% / 20 天（動量環境下適合稍寬的出場參數）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM009Config(ExperimentConfig):
    """IWM-009 Small-Cap Momentum Pullback 策略專屬參數"""

    pair_ticker: str = "SPY"
    # 相對強度：IWM 20d ret - SPY 20d ret >= threshold
    relative_return_lookback: int = 20
    relative_outperform_threshold: float = 0.03  # IWM - SPY >= 3%
    # 短期回檔
    pullback_days: int = 5
    pullback_threshold: float = -0.02  # 5日回檔 <= -2%
    # 趨勢確認
    sma_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> IWM009Config:
    return IWM009Config(
        name="iwm_009_momentum_rotation",
        experiment_id="IWM-009",
        display_name="IWM Small-Cap Momentum Pullback (IWM/SPY)",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.05,
        stop_loss=-0.045,
        holding_days=20,
    )
