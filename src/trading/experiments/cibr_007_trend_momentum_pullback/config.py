"""
CIBR 趨勢動量回調配置 (CIBR Trend Momentum Pullback Config)

策略方向：趨勢跟蹤（repo 中最少使用的方向）
不同於 CIBR-001~006 的均值回歸/突破/RS動量，本實驗買入確認上升趨勢中的
短期回調，假設趨勢延續將推動價格回升。

Att1 ★ Final: SMA50 + 5d PB≥2.5% + WR(5)≤-70, TP3.5%/SL3.5%/15d
  → Part A 0.25 (36 signals, 63.9% WR), Part B 0.34 (15 signals, 66.7% WR)
  → min(A,B) 0.25, A/B 訊號比 0.96:1（優秀）

Att2: +ATR(5)/ATR(20)>1.10 + PB 3.0% + SL -4.0%
  → Part A 0.23, Part B 0.03（ATR 過濾對趨勢策略反效果）

Att3: +SMA(20)>SMA(50) 金叉 + 持倉 18天
  → Part A 0.14, Part B 0.34（金叉僅移除 2 訊號，無效）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBRTrendMomentumConfig(ExperimentConfig):
    """CIBR 趨勢動量回調參數"""

    # 趨勢確認
    sma_period: int = 50  # SMA(50) 趨勢濾波

    # 回調進場
    pullback_lookback: int = 5  # 5日短期回調
    pullback_threshold: float = -0.025  # 回調 ≥ 2.5%（1.6σ）

    # 超賣確認
    wr_period: int = 5  # WR(5) 短週期
    wr_threshold: float = -70.0  # ≤ -70（較寬，趨勢提供品質）

    # 冷卻
    cooldown_days: int = 10  # 防止回調延續中連續進場


def create_default_config() -> CIBRTrendMomentumConfig:
    return CIBRTrendMomentumConfig(
        name="cibr_007_trend_momentum_pullback",
        experiment_id="CIBR-007",
        display_name="CIBR Trend Momentum Pullback",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%（對稱）
        holding_days=15,  # 15天（趨勢回調較快解決）
    )
