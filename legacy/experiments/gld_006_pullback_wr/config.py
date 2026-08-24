"""
GLD 回檔 + Williams %R 均值回歸配置 (GLD Pullback + Williams %R Mean Reversion Config)

以「10 日高點回檔幅度」取代 Keltner Channel 作為入場條件，搭配 Williams %R 確認超賣。
回檔幅度天然適應趨勢行情（參考點隨趨勢上移），解決 GLD-005 在強勢行情下
訊號稀疏的問題，使 Part A 與 Part B 訊號頻率更均衡。

Uses pullback from 10-day high instead of Keltner Channel for entry.
Pullback naturally adapts to trending markets (reference point moves with trend).
Solves GLD-005's signal scarcity in strong trends, balancing Part A / Part B frequency.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLDPullbackWRConfig(ExperimentConfig):
    """GLD 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥3% 觸發
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 7

    # 追蹤停損
    trail_activation_pct: float = 0.02  # 獲利 +2% 啟動
    trail_distance_pct: float = 0.015  # 追蹤距離 1.5%


def create_default_config() -> GLDPullbackWRConfig:
    return GLDPullbackWRConfig(
        name="gld_006_pullback_wr",
        experiment_id="GLD-006",
        display_name="GLD Pullback + Williams %R Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.03,  # +3.0%
        stop_loss=-0.04,  # -4.0%
        holding_days=20,  # 20 天
    )
