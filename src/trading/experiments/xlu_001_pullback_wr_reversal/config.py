"""
XLU 回檔 + Williams %R + 反轉K線確認配置
(XLU Pullback + Williams %R + Reversal Candle Confirmation Config)

XLU 日波動約 1.08%（≈ GLD 的 0.97 倍）。
進場使用 10 日高點回檔 ≥3% + Williams %R(10) ≤ -80 + 收盤位置 ≥ 40%。
固定 TP/SL 出場（不使用追蹤停損，避免過早截斷獲利）。

XLU daily vol ~1.08% (0.97x GLD). Fixed TP/SL exit (no trailing stop).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLUPullbackWRReversalConfig(ExperimentConfig):
    """XLU 回檔 + Williams %R + 反轉K線確認參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥3% 觸發
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 7

    # 收盤位置過濾
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4


def create_default_config() -> XLUPullbackWRReversalConfig:
    return XLUPullbackWRReversalConfig(
        name="xlu_001_pullback_wr_reversal",
        experiment_id="XLU-001",
        display_name="XLU Pullback + Williams %R + Reversal Candle",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.04,  # -4.0%（非對稱寬停損）
        holding_days=20,  # 20 天
    )
