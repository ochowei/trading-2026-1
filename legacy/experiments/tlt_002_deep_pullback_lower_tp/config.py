"""
TLT 回檔 + WR + 反轉K線 + 中期跌幅過濾均值回歸配置
(TLT Pullback + WR + Reversal + Medium-term Drawdown Filter Config)

基於 TLT-001 改進：加入 60 日跌幅 <= 10% 過濾器，
區分「正常環境回檔」與「持續性熊市回檔」。
2022 升息期 TLT 60 日跌幅常超過 10%，此過濾器可大量移除假訊號。
其餘參數維持 TLT-001 原值。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLTDeepPullbackLowerTPConfig(ExperimentConfig):
    """TLT 回檔 + WR + 反轉K線 + 中期跌幅過濾參數"""

    # 回檔範圍進場（同 TLT-001）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-001）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-001）
    close_position_threshold: float = 0.4

    # 中期跌幅過濾（新增）
    medium_term_lookback: int = 60  # 60 個交易日
    medium_term_max_drawdown: float = -0.10  # 60 日跌幅不超過 10%

    # 冷卻期（同 TLT-001）
    cooldown_days: int = 7


def create_default_config() -> TLTDeepPullbackLowerTPConfig:
    return TLTDeepPullbackLowerTPConfig(
        name="tlt_002_deep_pullback_lower_tp",
        experiment_id="TLT-002",
        display_name="TLT Pullback + WR + Reversal + Drawdown Filter",
        tickers=["TLT"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（同 TLT-001）
        stop_loss=-0.035,  # -3.5%（同 TLT-001）
        holding_days=20,  # 20 天（同 TLT-001）
    )
