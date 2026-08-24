"""
EWZ-004: Short-Window WR Mean Reversion
(EWZ 短窗口 WR 均值回歸)

策略方向：均值回歸（WR 週期優化，AI_CONTEXT 列為尚未嘗試的方向）

Att1: 趨勢動量回檔（Close>SMA50 + 4-8% pullback + WR≤-60）
  → Part A Sharpe 0.09, Part B 0.06。趨勢回檔在 EM ETF 上 WR 接近 50%，無邊際
  → 結論：趨勢確認對 EWZ 無效，宏觀事件可突然反轉趨勢

Att2: RSI(2)<10 + 7-10% 回檔 + ATR>1.1 + ClosePos≥40% + TP+5%/SL-4%/18d
  → Part A Sharpe -0.16 (WR 37.5%, 8訊號), Part B 10.63 (2訊號)
  → RSI(2) 在 EWZ 上完全失敗（lesson #27 驗證），1.75% vol EM 單國 ETF 不適用

Att3: WR(5)≤-80 + 回檔 7-10% + ClosePos≥40% + TP+5%/SL-4%/18d（無 ATR）
  假設：WR(5) 自然選擇急跌（close 必須在 5 日最低 20% 區間），
  可能使 ATR 過濾冗餘，同時捕捉不同於 WR(10) 的訊號集。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ004Config(ExperimentConfig):
    """EWZ-004 短窗口 WR 均值回歸參數"""

    # 回檔參數
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 10日高點回檔 >= 7%
    pullback_cap: float = -0.10  # 回檔上限 10%

    # Williams %R 參數（短窗口）
    wr_period: int = 5  # WR(5) 替代 WR(10)，捕捉更近期的動量崩潰
    wr_threshold: float = -80.0  # WR(5) <= -80

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EWZ004Config:
    return EWZ004Config(
        name="ewz_004_trend_momentum_pullback",
        experiment_id="EWZ-004",
        display_name="EWZ Short-Window WR Mean Reversion",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（同 EWZ-002 最佳）
        stop_loss=-0.040,  # -4.0%
        holding_days=18,  # 18 天（同 EWZ-002 最佳）
    )
