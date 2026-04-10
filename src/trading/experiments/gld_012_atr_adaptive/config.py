"""
GLD-012: 無追蹤停損均值回歸（No-Trailing-Stop Mean Reversion）

基於 GLD-008 框架（20日回檔 + WR + 反轉K線），移除追蹤停損。
GLD-008 有 6+ 筆交易被追蹤停損截斷在 +0.47%~+1.32%，
理論上部分可以繼續上漲到 TP +3.0%。

嘗試記錄：
- Att1: ATR > 1.1 + 追蹤停損 → Part A 0.38 (21訊號), Part B 0.00 (僅2訊號)。太嚴格。
- Att2: ATR > 1.05 + 追蹤停損 → Part A 0.22 (23訊號, WR 69.6%), Part B 1.83 (5訊號)。
  ATR 過濾在 GLD 無效：低波動拉回（ATR ratio < 1.05）反而是最好的均值回歸訊號。
- Att3: 移除 ATR 過濾 + 移除追蹤停損，同 GLD-008 進場，純 TP/SL/到期出場。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD012Config(ExperimentConfig):
    """GLD 無追蹤停損均值回歸參數"""

    # 進場指標（同 GLD-008）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.03  # 回檔 ≥3%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80
    cooldown_days: int = 7

    # 收盤位置過濾（同 GLD-008）
    close_position_threshold: float = 0.4


def create_default_config() -> GLD012Config:
    return GLD012Config(
        name="gld_012_atr_adaptive",
        experiment_id="GLD-012",
        display_name="GLD No-Trailing-Stop Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 GLD-008）
        stop_loss=-0.04,  # -4.0%（同 GLD-008）
        holding_days=20,  # 20 天（同 GLD-008）
    )
