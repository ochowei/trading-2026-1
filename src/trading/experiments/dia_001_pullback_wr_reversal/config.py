"""
DIA 回檔 + Williams %R + 反轉K線確認配置
(DIA Pullback + Williams %R + Reversal Candle Confirmation Config)

基於 GLD-007 策略模板，DIA 日波動度約 1.0-1.3%（與 GLD ~1.2% 相近），
參數直接沿用 GLD-007 設定作為起點。

Based on GLD-007 template. DIA daily volatility ~1.0-1.3% (comparable to GLD ~1.2%),
so parameters start at GLD-007 values with minimal adjustment.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIAPullbackWRReversalConfig(ExperimentConfig):
    """DIA 回檔 + Williams %R + 反轉K線確認參數"""

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


def create_default_config() -> DIAPullbackWRReversalConfig:
    return DIAPullbackWRReversalConfig(
        name="dia_001_pullback_wr_reversal",
        experiment_id="DIA-001",
        display_name="DIA Pullback + Williams %R + Reversal Candle",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=20,  # 20 天
    )
