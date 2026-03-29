"""
SIVR RSI(2) + 回檔範圍均值回歸配置 (SIVR RSI(2) + Capped Pullback Mean Reversion Config)

實驗結果：❌ 三次嘗試均未能超越 SIVR-003。
- Att1: RSI(2)<15 + 2日跌幅≥3% + 回檔上限 15% → Part A Sharpe 0.27 但 Part B 崩潰至 0.09
- Att2: RSI(2)<20 + 回檔上限 + SL -4.0% → 全面劣化，Part A Sharpe 0.05
- Att3: RSI(2)<15 + 回檔上限（無2日跌幅）→ Part A/B Sharpe 0.15/0.18 均低於 SIVR-003

結論：WR(10) 的寬視角在 SIVR 高波動環境下提供更好的進場時機，
RSI(2) 替換後訊號日期偏移導致 Part B 品質下降。

Experiment result: ❌ All 3 attempts failed to beat SIVR-003.
RSI(2) produces different signal timing that consistently hurts Part B OOS performance.
WR(10)'s broader oversold view works better for silver's high-volatility mean reversion.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRRSI2PullbackConfig(ExperimentConfig):
    """SIVR RSI(2) + 回檔範圍均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    pullback_cap: float = -0.15  # 回檔上限 15%（過濾極端崩盤）
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    decline_2d_threshold: float = 0.0  # 停用（Att1 證明對 Part B 有害）
    cooldown_days: int = 10


def create_default_config() -> SIVRRSI2PullbackConfig:
    return SIVRRSI2PullbackConfig(
        name="sivr_004_rsi2_pullback",
        experiment_id="SIVR-004",
        display_name="SIVR RSI(2) + Capped Pullback Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,
    )
