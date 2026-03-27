"""
SPY 回檔 + Williams %R + 反轉K線確認配置
(SPY Pullback + Williams %R + Reversal Candle Confirmation Config)

基於 GLD-007 模板，適用於 SPY（S&P 500 ETF）。
SPY 與 GLD 日波動率相近（~1.0-1.2%），故參數幾乎不需縮放。

Based on GLD-007 template for SPY (S&P 500 ETF).
SPY and GLD have similar daily volatility (~1.0-1.2%), so minimal parameter scaling.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYPullbackWRConfig(ExperimentConfig):
    """SPY 回檔 + Williams %R + 反轉K線確認參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥3% 觸發
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 7

    # 收盤位置過濾
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4

    # 追蹤停損
    trail_activation_pct: float = 0.02  # 獲利 +2% 啟動
    trail_distance_pct: float = 0.015  # 追蹤距離 1.5%


def create_default_config() -> SPYPullbackWRConfig:
    return SPYPullbackWRConfig(
        name="spy_001_pullback_wr",
        experiment_id="SPY-001",
        display_name="SPY Pullback + Williams %R + Reversal Candle",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=20,  # 20 天
    )
