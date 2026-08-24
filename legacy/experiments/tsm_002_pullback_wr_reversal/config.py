"""
TSM 回檔 + Williams %R + 反轉K線確認配置
TSM Pullback + Williams %R + Reversal Candle Configuration

改良自 GLD-007 架構，針對 TSM 較高波動度（日波動 ~2.5%）調整參數：
- 回檔閾值放寬至 -8%（GLD-007 為 -3%）
- TP/SL 放大至 +7%/-7%（GLD-007 為 +3.5%/-4%）
- 不使用追蹤停損（日波動 > 1.5% 不適用，見 cross_asset_lessons #2）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMPullbackWRReversalConfig(ExperimentConfig):
    """TSM 回檔 + Williams %R + 反轉K線確認參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 ≥10% 觸發（過濾淺回檔假訊號）
    wr_period: int = 10
    wr_threshold: float = -85.0  # Williams %R ≤ -85 (更嚴格超賣)
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4
    cooldown_days: int = 10


def create_default_config() -> TSMPullbackWRReversalConfig:
    return TSMPullbackWRReversalConfig(
        name="tsm_002_pullback_wr_reversal",
        experiment_id="TSM-002",
        display_name="TSM Pullback + Williams %R + Reversal Candle",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.07,  # +7%（半導體反彈力道佳但不宜過貪）
        stop_loss=-0.07,  # -7%（對稱 TP/SL）
        holding_days=20,  # 20 天
    )
