"""
EEM-003: Volatility-Adaptive RSI(2) with Deep Decline Filter
(EEM 波動率自適應 RSI(2) + 深度急跌過濾)

EEM-002 發現：
- ATR>1.15 有效過濾 Part B 壞訊號（100% WR）
- 移除 ClosePos 大幅改善 Part B（1.48 Sharpe, 12 信號, +34.13%）但傷 Part A
- Part A 的問題：EM 熊市（2019-2023）慢跌產生假均值回歸訊號

本實驗：移除 ClosePos + 加深 2日跌幅門檻（2.0%→替代 ClosePos 的過濾功能）
+ ATR>1.15 + SL-3.0%。深跌幅門檻確保只在急速恐慌拋售時進場。

Att1: 2日跌幅 ≥ 2.0%, 無 ClosePos, ATR>1.15 → Part A -0.19/Part B 1.11, 深跌幅無法補償 ClosePos
Att2: ClosePos≥40% + ATR>1.15, 2日跌幅 1.5%, 冷卻10天 → Part A 0.06/Part B 0.00(100%WR) ★
Att3: 無 ClosePos + ATR>1.15, 2日跌幅 1.5%, 冷卻10天 → Part A -0.19/Part B 1.48, 同 Att1
Final: Att2 is best — ClosePos essential for Part A, cooldown 10 suppresses COVID cascade
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM003Config(ExperimentConfig):
    """EEM-003 波動率自適應 RSI(2) + 深度急跌過濾"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期（加長至 10 天，阻斷下跌趨勢中的連續進場）
    cooldown_days: int = 10


def create_default_config() -> EEM003Config:
    return EEM003Config(
        name="eem_003_vol_adaptive_deep_decline",
        experiment_id="EEM-003",
        display_name="EEM Vol-Adaptive RSI(2) Deep Decline",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
