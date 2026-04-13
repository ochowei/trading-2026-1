"""
INDA-004: Trend Pullback (趨勢回調買入)

策略類型：動量/趨勢回調（非均值回歸）
核心假設：INDA 受印度經濟長期成長驅動，存在結構性上升趨勢。
上升趨勢中的回調多為暫時性修正，提供買入機會。
與均值回歸不同，本策略明確要求上升趨勢背景，避免在下跌趨勢中接刀。

Att1: SMA(50), PB 2.5-6%, WR <= -70, TP +3.0%, SL -3.0%, 15d, cd10
  → Part A -0.09 / Part B 0.48（SMA(50) 趨勢濾波過鬆，橫盤市場產生大量假訊號）
Att2: SMA(50) slope(10d) + PB 3-7%, WR <= -80, TP +3.5%, SL -4.0%, 18d, cd10
  → Part A 0.06 / Part B 0.51（SMA 斜率改善，但 10 日回看太短，2022 訊號仍滑過）
Att3: SMA(50) slope(20d) + PB 3-7%, WR <= -80, TP +4.0%, SL -4.0%, 20d, cd10
  → Part A 0.31 / Part B 0.50，min(A,B) 0.31（vs INDA-002 的 0.15，+107%）
  20 日斜率有效過濾 2022 初期熊市訊號
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDATrendPullbackConfig(ExperimentConfig):
    """INDA 趨勢回調策略參數"""

    # 趨勢確認 (Trend confirmation)
    sma_trend_period: int = 50
    sma_slope_lookback: int = 20  # SMA 斜率回看天數（20d 比 10d 更能捕捉趨勢轉折）

    # 回調參數 (Pullback parameters)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回調 >= 3%
    pullback_cap: float = -0.07  # 回調 <= 7%（隔離崩盤）

    # Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 冷卻期 (Cooldown)
    cooldown_days: int = 10


def create_default_config() -> INDATrendPullbackConfig:
    return INDATrendPullbackConfig(
        name="inda_004_trend_pullback",
        experiment_id="INDA-004",
        display_name="INDA Trend Pullback",
        tickers=["INDA"],
        data_start="2018-01-01",
        profit_target=0.04,  # +4.0%
        stop_loss=-0.04,  # -4.0%
        holding_days=20,
    )
