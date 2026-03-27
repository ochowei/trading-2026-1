"""
SPY-002: 回檔 + Williams %R + 反轉K線（無追蹤停損版）
(SPY Pullback + WR + Reversal Candle, No Trailing Stop)

基於 SPY-001 改進：移除追蹤停損、降低止盈、收緊止損、縮短持倉。
SPY-001 的問題是追蹤停損過早出場（9/20 筆），獲利交易僅 +0.5~1.8%，
無法抵銷 -4.1% 的停損虧損。

改動：
- 移除追蹤停損（讓獲利交易完整達標）
- 止盈 +3.5% → +2.5%（更符合 SPY 低波動特性）
- 止損 -4.0% → -2.5%（與 TP 對稱的 1:1 風險報酬比）
- 持倉 20 天 → 15 天（SPY 均值回歸速度較快）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYNoTrailingConfig(ExperimentConfig):
    """SPY 回檔 + Williams %R + 反轉K線（無追蹤停損）參數"""

    # 進場指標（與 SPY-001 相同）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥3% 觸發
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 7

    # 收盤位置過濾（與 SPY-001 相同）
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4


def create_default_config() -> SPYNoTrailingConfig:
    return SPYNoTrailingConfig(
        name="spy_002_no_trailing",
        experiment_id="SPY-002",
        display_name="SPY Pullback + WR + Reversal (No Trailing Stop)",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.025,  # -2.5% (與 TP 對稱)
        holding_days=15,  # 15 天 (縮短，SPY 回歸較快)
    )
