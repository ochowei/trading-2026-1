"""
EWZ-002: Volatility-Adaptive Pullback + WR Mean Reversion
(EWZ 波動率自適應回檔均值回歸)

在 EWZ-001 的 pullback+WR 基礎上加入三層過濾 + 非對稱出場：
1. ATR(5)/ATR(20) > 1.1 選擇急跌恐慌（過濾慢磨下跌假訊號）
2. ClosePos >= 40% 確認日內反轉（過濾持續下跌中的假超賣）
3. 回檔上限 10%（隔離 COVID 等極端崩盤訊號）
4. TP +5% / SL -4% 非對稱出場（盈虧比 1.25:1）

Att1: ATR > 1.1 + ClosePos + cap + TP+4%/SL-4%/15d
  → Part A Sharpe 0.22 (WR 61.5%, 13訊號), Part B Sharpe 2.55 (WR 100%, 4訊號)
  → min(A,B) 0.22（vs EWZ-001 的 0.10，+120%）

Att2: ATR > 1.15（更高門檻）
  → Part A Sharpe 0.19 (10訊號，移除 2 贏 1 輸)，Part B 不變
  → 退化，ATR 1.15 過度過濾好訊號

Att3★: ATR > 1.1 + TP+5%/SL-4%/18d（非對稱出場）
  → Part A Sharpe 0.34 (WR 61.5%, 累計+19.84%), Part B Sharpe 12.85 (WR 100%, 累計+20.56%)
  → min(A,B) 0.34（+240% vs EWZ-001），A/B 累計差距 0.72%
  → Profit factor 1.95，所有 8 筆贏利交易均輕鬆達到 +5%
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ002Config(ExperimentConfig):
    """EWZ-002 波動率自適應回檔均值回歸參數"""

    # 回檔參數（同 EWZ-001）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 10日高點回檔 >= 7%
    pullback_cap: float = -0.10  # 回檔上限 10%（隔離極端崩盤）

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.1  # ATR(5)/ATR(20) > 1.1

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EWZ002Config:
    return EWZ002Config(
        name="ewz_002_vol_adaptive_pullback",
        experiment_id="EWZ-002",
        display_name="EWZ Volatility-Adaptive Pullback MR",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（非對稱出場，提高盈虧比）
        stop_loss=-0.040,  # -4.0%
        holding_days=18,  # 延長持倉，給予更多時間達到較高 TP
    )
