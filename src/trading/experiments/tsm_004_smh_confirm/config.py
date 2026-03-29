"""
TSM 半導體指數確認配置
TSM Semiconductor Index (SMH) Confirmation Configuration

基於 TSM-002 架構，加入 SMH 回檔確認減少個股特定因素假訊號，
並測試非對稱 TP/SL 以利用 TSM 的高波動反彈力道。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMSMHConfirmConfig(ExperimentConfig):
    """TSM 半導體指數確認參數"""

    # TSM 進場指標（沿用 TSM-002）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # TSM 回檔 ≥10%
    wr_period: int = 10
    wr_threshold: float = -85.0  # WR(10) ≤ -85
    close_position_threshold: float = 0.4  # ClosePos ≥ 40%
    cooldown_days: int = 10

    # 回檔上限（過濾極端崩盤訊號）
    pullback_upper_threshold: float = -0.20  # 回檔 ≤ 20% 才進場，> 20% 視為自由落體


def create_default_config() -> TSMSMHConfirmConfig:
    return TSMSMHConfirmConfig(
        name="tsm_004_smh_confirm",
        experiment_id="TSM-004",
        display_name="TSM Pullback + WR + Capped Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.07,  # +7%（沿用 TSM-002）
        stop_loss=-0.07,  # -7%（沿用 TSM-002）
        holding_days=20,
    )
