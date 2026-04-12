"""
VGK-004: Volatility-Adaptive Pullback + Williams %R Mean Reversion
(VGK 波動率自適應回檔+WR 均值回歸)

從 RSI(2) 框架切換至 pullback+WR 框架（XLU-011 模板）：
- VGK vol 1.12% ≈ XLU 1.0%，XLU-011 用 pullback+WR+ATR 達到 Sharpe 0.67
- 10 日回檔 ≥ 3%（VGK ~2.7σ/day，比 XLU 3.5% 稍淺，匹配 VGK 震幅）
- 回檔上限 7%（隔離極端崩盤如 COVID）
- WR(10) ≤ -80 + ClosePos ≥ 40%（超賣+反轉確認）
- ATR(5)/ATR(20) > 1.15（區分急跌 vs 慢磨，XLU-011 甜蜜點）
- TP +3.0% / SL -3.5% / 25 天（DIA-005 出場優化）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK004Config(ExperimentConfig):
    """VGK-004 波動率自適應回檔+WR 均值回歸參數"""

    # 回檔參數
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_cap: float = -0.07  # 回檔 <= 7%

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉K線確認）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> VGK004Config:
    return VGK004Config(
        name="vgk_004_vol_adaptive_pullback_wr",
        experiment_id="VGK-004",
        display_name="VGK Vol-Adaptive Pullback+WR",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.035,  # -3.5%（DIA-005 參考）
        holding_days=25,  # 25 天（延長持倉）
    )
