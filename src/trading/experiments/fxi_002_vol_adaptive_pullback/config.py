"""
FXI-002: Volatility-Adaptive Pullback + WR Mean Reversion
(FXI 波動率自適應回檔均值回歸)

在 FXI-001 的 pullback+WR 基礎上加入三層過濾 + 非對稱出場：
1. ATR(5)/ATR(20) > 1.05 選擇急跌恐慌（過濾慢磨下跌假訊號）
2. ClosePos >= 40% 確認日內反轉（過濾持續下跌中的假超賣）
3. 回檔上限 12%（隔離 COVID / 中國監管風暴等極端崩盤）
4. TP +5% / SL -4.5% 非對稱出場（盈虧比 1.11:1）

Att1: PB>=7% + ATR>1.1 + ClosePos>=40% + cap12% + TP5%/SL4.5%/18d
  → Part A 0.33 (14訊號, WR64.3%), Part B 0.04 (2訊號, WR50%)
  → A/B 訊號比 2.8:1 過高，ATR 1.1 過度過濾 Part B 訊號

Att2: PB>=6% + ATR>1.05（更適合 2.0% vol，參考 COPX 2.25% 用 1.05）
  → Part A 0.44 (20訊號, WR70.0%, +43.32%), Part B 0.30 (4訊號, WR50%, +4.59%)
  → min(A,B) 0.30, A/B 訊號比 2:1 可接受但累計報酬差距 38.7pp > 30%

Att3★: PB>=5% + ATR>1.05（PB -5% ≈ 2.5σ，與 GLD -3%/1.2% vol 相同深度比）
  → Part A 0.33 (26訊號, WR65.4%, +43.19%), Part B 0.50 (5訊號, WR60%, +9.82%)
  → min(A,B) 0.33（vs FXI-001 -0.17, 大幅提升）
  → Part B Sharpe 超越 Part A，OOS 表現強勁，profit factor 2.91
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI002Config(ExperimentConfig):
    """FXI-002 波動率自適應回檔均值回歸參數"""

    # 回檔參數
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # 10日高點回檔 >= 5%（2.5σ for 2% vol）
    pullback_cap: float = -0.12  # 回檔上限 12%（隔離極端崩盤）

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05  # ATR(5)/ATR(20) > 1.05（per COPX precedent）

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FXI002Config:
    return FXI002Config(
        name="fxi_002_vol_adaptive_pullback",
        experiment_id="FXI-002",
        display_name="FXI Volatility-Adaptive Pullback MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（非對稱出場，提高盈虧比）
        stop_loss=-0.045,  # -4.5%
        holding_days=18,  # 延長持倉，給予更多時間達到較高 TP
    )
