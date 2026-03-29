"""
TLT 回檔範圍 + Williams %R + 反轉K線均值回歸配置
(TLT Pullback Range + Williams %R + Reversal Candle Config)

基於 GLD-007 進場條件 + USO-012/013 的回檔範圍過濾概念。
TLT 日波動約 1.00%，2022 利率上升期經歷極端回撤（>10%），
回檔範圍上限 7% 可過濾持續性下跌環境中的假訊號。

Based on GLD-007 entry + USO-012/013 pullback range concept.
TLT daily vol ~1.00%. Upper pullback cap 7% filters sustained selloff signals.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLTPullbackWRReversalConfig(ExperimentConfig):
    """TLT 回檔範圍 + Williams %R + 反轉K線確認參數"""

    # 回檔範圍進場
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥ 3% 觸發
    pullback_upper: float = -0.07  # 回檔 ≤ 7%（過濾極端下跌）

    # Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)

    # 收盤位置過濾
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLTPullbackWRReversalConfig:
    return TLTPullbackWRReversalConfig(
        name="tlt_001_pullback_wr_reversal",
        experiment_id="TLT-001",
        display_name="TLT Pullback Range + Williams %R + Reversal Candle",
        tickers=["TLT"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=20,  # 20 天
    )
