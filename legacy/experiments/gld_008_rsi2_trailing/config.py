"""
GLD-008: 20 日回檔 + Williams %R + 反轉K線 + 追蹤停損
(GLD 20-Day Pullback + Williams %R + Reversal Candle + Trailing Stop)

基於 GLD-007，改用 20 日回看窗口取代 10 日。
COPX-003 在類似改動下 Sharpe 提升 100%（0.19→0.39），
更長回看窗口捕捉更有意義的回檔，過濾短期噪音。

三次嘗試記錄：
- Att1: RSI(2)<10 + 2日跌幅≥1.5% + ClosePos≥40%（改用 RSI(2) 進場）
  → Part A Sharpe 0.28 / Part B 1.59（RSI(2) 在 GLD 產生更少且更差的訊號）
- Att2: 20日回看 + 回檔≥3% + WR≤-80 + ClosePos≥40%（同 GLD-007 進場，改回看窗口）
  → Part A Sharpe 0.43 / Part B 2.02（20日回看改善 Part A，較 GLD-007 的 0.41 提升）
- Att3: 同 Att2 進場，TP +3.0%（降低 TP 讓更多交易直接達標而非被追蹤停損截斷）
  → Part A Sharpe 0.45 / Part B 2.33（**新最佳**，超越 GLD-007 的 0.41/2.04）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD008Config(ExperimentConfig):
    """GLD 20日回檔 + WR + 反轉K線參數"""

    # 進場指標（同 GLD-007，僅改回看窗口）
    pullback_lookback: int = 20  # 20日回看（GLD-007 為 10 日）
    pullback_threshold: float = -0.03  # 回檔 ≥3% 觸發
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80
    cooldown_days: int = 7

    # 收盤位置過濾（同 GLD-007）
    close_position_threshold: float = 0.4

    # 追蹤停損（同 GLD-007）
    trail_activation_pct: float = 0.02  # 獲利 +2% 啟動
    trail_distance_pct: float = 0.015  # 追蹤距離 1.5%


def create_default_config() -> GLD008Config:
    return GLD008Config(
        name="gld_008_rsi2_trailing",
        experiment_id="GLD-008",
        display_name="GLD 20-Day Pullback + WR + Reversal + Trailing Stop",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（降低 TP 讓更多交易直接達標）
        stop_loss=-0.04,  # -4.0%（同 GLD-007）
        holding_days=20,  # 20 天（同 GLD-007）
    )
