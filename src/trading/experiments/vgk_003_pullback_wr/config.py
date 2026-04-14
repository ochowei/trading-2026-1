"""
VGK-003: 回檔 + Williams %R + ATR 波動率自適應均值回歸
(VGK Pullback + Williams %R + ATR Volatility-Adaptive Mean Reversion)

結合 pullback+WR 框架與 ATR 波動率過濾：
- Pullback+WR 捕捉 10 日回檔，比 RSI(2) 的 2 日急跌更穩健
- ATR(5)/ATR(20) > 1.15 過濾緩跌訊號（2022 歐洲危機的主要失敗模式）

Att1（無 ATR）: Part A 0.09 / Part B 0.57（Part A 31 訊號中 12 停損）
Att2（加 ATR > 1.15）: 預期移除 Part A 慢磨下跌期的停損訊號
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK003Config(ExperimentConfig):
    """VGK-003 回檔 + Williams %R + ATR 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥ 3% 觸發（同 EWJ-001）

    # Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) ≤ -80（超賣）

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # ≥ 40%

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15  # XLU-011 甜蜜點（VGK vol 1.12% ≈ XLU 1.0%）

    # 冷卻期
    cooldown_days: int = 7  # 7 天（避免危機期間訊號聚集）


def create_default_config() -> VGK003Config:
    return VGK003Config(
        name="vgk_003_pullback_wr",
        experiment_id="VGK-003",
        display_name="VGK Pullback + Williams %R + ATR",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 EWJ-001）
        stop_loss=-0.040,  # -4.0%（同 EWJ-001，比 VGK-001 寬 1%）
        holding_days=20,
    )
