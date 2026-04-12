"""
EEM-004: Pullback + Williams %R Mean Reversion
(EEM 回檔範圍 + Williams %R 均值回歸)

EEM 前 3 個實驗均使用 RSI(2) 框架，Part A Sharpe 最高僅 0.06。
本實驗改用 GLD-012 驗證有效的 pullback+WR 框架：
- EEM 日波動 1.17% 與 GLD 1.12% 近似，參數可直接移植
- Lesson #16 指出指數 ETF 不適合 pullback+WR，但該結論基於 IWM 的淺回檔
- EEM 受 EM 事件驅動（貿易戰、COVID、地緣政治），有深回檔特性，更接近 GLD
- 回檔框架可能比 RSI(2) 更好地過濾 EM 慢跌假訊號

Att1: pullback 20d ≥3% + WR(10)≤-80 + ClosePos≥40% + cooldown 10
  → Part A 0.01 (45訊號, WR 51.1%), Part B 0.27 (12訊號, WR 66.7%)
  問題：Part A 訊號過多（9.0/yr），慢跌假訊號拖累績效

Att2: + ATR(5)/ATR(20)>1.15 過濾慢跌 + 回檔上限 -8% 過濾極端崩盤
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM004Config(ExperimentConfig):
    """EEM-004 回檔範圍 + Williams %R 均值回歸參數"""

    # 回檔參數（同 GLD-012）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.03  # 回檔 >= 3%

    # Williams %R 參數（同 GLD-012）
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 回檔上限（過濾極端崩盤，lesson #13: 5-6σ ≈ 7-8% for 1.17% vol）
    pullback_cap: float = -0.08  # 回檔 <= 8%

    # 收盤位置過濾（EEM 已驗證有效）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（EEM-003 驗證 ATR>1.15 有效）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期（EEM-003 驗證 10 天最佳）
    cooldown_days: int = 10


def create_default_config() -> EEM004Config:
    return EEM004Config(
        name="eem_004_pullback_wr",
        experiment_id="EEM-004",
        display_name="EEM Pullback + Williams %R Mean Reversion",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
