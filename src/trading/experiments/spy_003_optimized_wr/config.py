"""
SPY-003: 回檔 + Williams %R + VIX 恐慌過濾
(SPY Pullback + WR + VIX Fear Filter)

基於 SPY-002 改進，加入 VIX ≥ 20 過濾，並放寬回檔門檻至 2.5%。

結果：Part B 表現亮眼（100% WR, +13.14%），A/B 訊號平衡佳（1.28:1），
但 Part A 為負（-1.31%）。VIX 過濾在牛市修正期表現優異，
但在熊市中無法有效區分好壞訊號（因為 VIX 在熊市持續偏高）。

結論：不優於 SPY-002 整體表現，記錄為嘗試性實驗。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYVixFilterConfig(ExperimentConfig):
    """SPY 回檔 + WR + VIX 恐慌過濾參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.025  # 回檔 ≥2.5%（放寬，VIX 補償品質）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80
    cooldown_days: int = 7

    # 收盤位置過濾
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4

    # VIX 恐慌過濾
    vix_threshold: float = 20.0  # VIX ≥ 20 才進場


def create_default_config() -> SPYVixFilterConfig:
    return SPYVixFilterConfig(
        name="spy_003_optimized_wr",
        experiment_id="SPY-003",
        display_name="SPY Pullback + WR + VIX Fear Filter",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.025,  # -2.5%
        holding_days=15,  # 15 天
    )
