"""
EWT-003: BB Squeeze Breakout
(EWT 布林帶擠壓突破)

EWT-001/002 均為均值回歸策略，Part A Sharpe 0.10/0.13。
本實驗嘗試完全不同的策略類型：突破。

設計理據：
- EWT 半導體權重極高（TSM>20%），半導體週期驅動方向性突破
- EWT 日波動 1.41% 處於 BB Squeeze 有效邊界（EEM 1.17% 有效，INDA 0.97% 失敗）
- 突破策略迴避熊市連續下跌問題（不在下跌中買入）
- 參數參考 EEM-005 Att2 框架（30th pct squeeze），按 EWT 波動度 (1.41%/1.17%=1.21x) 縮放
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT003Config(ExperimentConfig):
    """EWT-003 BB 擠壓突破參數"""

    # 布林帶參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 擠壓偵測
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30  # 30th percentile
    bb_squeeze_recent_days: int = 5

    # 趨勢確認
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EWT003Config:
    return EWT003Config(
        name="ewt_003_bb_squeeze_breakout",
        experiment_id="EWT-003",
        display_name="EWT BB Squeeze Breakout",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（EEM 3.0% × 1.21 vol ratio ≈ 3.6%）
        stop_loss=-0.035,  # -3.5%（對稱 SL）
        holding_days=20,
    )
