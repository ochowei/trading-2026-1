"""
TSM-003: 回檔 + RSI(2) 極端超賣均值回歸
(TSM Pullback + RSI(2) Extreme Oversold Mean Reversion)

混合架構：結合 TSM-002 的回檔深度過濾（阻擋淺回檔假訊號）
與 RSI(2) 短期動量耗竭計時，達到更精確的進場。

- 回檔 ≥ 8%（10日高點）確保結構性下跌
- RSI(2) < 15 確認短期動量耗竭
- ClosePos ≥ 40% 日內反轉確認
- 不用追蹤停損（日波動 > 1.5%，見 cross_asset_lessons #2）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMRsi2Config(ExperimentConfig):
    """TSM 回檔 + RSI(2) 極端超賣均值回歸參數"""

    # 回檔深度過濾
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 ≥ 8%

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) >= 40%

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> TSMRsi2Config:
    return TSMRsi2Config(
        name="tsm_003_rsi2_reversal",
        experiment_id="TSM-003",
        display_name="TSM RSI(2) Extreme Oversold Reversal",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.06,  # +6%
        stop_loss=-0.06,  # -6%（對稱）
        holding_days=15,
    )
