"""
DIA-008: 20-day Pullback Range + Williams %R
(DIA 20 日回檔範圍均值回歸)

Attempt 3 — 策略轉向：動量策略在 DIA 上失敗（Att1/Att2 Sharpe 均為負），
改用跨資產驗證過的 20 日回檔範圍框架（COPX-003 Sharpe 0.39/0.35，
GLD-008 Sharpe 0.45/2.33 均採用 20 日回看）。

DIA-001 使用 10 日 pullback + WR + trailing stop 失敗（2022 熊市連續停損）。
本實驗的關鍵差異：
1. 20 日回看（vs 10 日）— 捕捉更有意義的回檔
2. 回檔上限 7%（vs 無上限）— 過濾熊市崩盤訊號
3. 固定出場 TP+3.0%/SL-3.5%/25d（vs trailing stop）— DIA-005 驗證最佳
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA008PullbackRangeConfig(ExperimentConfig):
    """DIA-008 20-day Pullback Range 策略專屬參數"""

    # 回檔範圍：20 日高點回檔
    pullback_lookback: int = 20
    pullback_min: float = 0.03  # 回檔 >= 3%
    pullback_max: float = 0.07  # 回檔 <= 7%

    # Williams %R 超賣確認
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（日內反轉確認）
    close_position_threshold: float = 0.4  # ClosePos >= 40%

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> DIA008PullbackRangeConfig:
    return DIA008PullbackRangeConfig(
        name="dia_008_momentum_pullback",
        experiment_id="DIA-008",
        display_name="DIA 20-day Pullback Range + WR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0% (DIA sweet spot)
        stop_loss=-0.035,  # -3.5% (DIA sweet spot)
        holding_days=25,  # 25d (DIA-005 validated)
    )
