"""
XLU-006: Pullback + WR + TLT Rate Regime Filter
(XLU 回檔 + WR + TLT 利率環境過濾)

Att1 失敗：RSI(2)<10 + 2日跌幅≥1.0% + ClosePos≥40%, TP+2.5%/SL-4.0%/20d
  Part A Sharpe -0.33, Part B Sharpe -0.73
  結論：SL-4.0% 也無法拯救 RSI(2) 在 XLU 的差訊號品質

Att2 失敗：XLU-003 進場 + 60日 XLU 跌幅過濾（≤10%）
  Part A Sharpe 0.02, Part B Sharpe 0.35
  結論：XLU 自身 60日 ROC 無法有效區分升息結構性下跌，Part A 同 XLU-003

Att3：XLU-003 進場 + TLT 60日 ROC > -5%（利率環境過濾）
  假說：TLT 直接追蹤利率，能更精確過濾升息期間的假均值回歸訊號。
  與 XLU-005 Att3 不同之處：那是用 TLT 為訊號源，這是用 TLT 為過濾器。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU006Config(ExperimentConfig):
    """XLU 回檔 + WR + TLT 利率過濾參數"""

    # 回檔參數（同 XLU-003）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035  # 回檔 >= 3.5%
    pullback_cap: float = -0.07  # 回檔 <= 7%

    # Williams %R 參數（同 XLU-003）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 XLU-003）
    close_position_threshold: float = 0.4

    # TLT 利率環境過濾（新增）
    tlt_ticker: str = "TLT"
    tlt_roc_period: int = 60
    tlt_roc_threshold: float = -0.05  # TLT 60日 ROC > -5%

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> XLU006Config:
    return XLU006Config(
        name="xlu_006_rsi2_wide_sl",
        experiment_id="XLU-006",
        display_name="XLU Pullback + WR + TLT Rate Filter",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
