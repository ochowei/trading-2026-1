"""
INDA-004: 短期動量崩潰均值回歸
(INDA Short-term Momentum Crash Mean Reversion)

全新進場架構：使用短期動量崩潰（WR + 2日急跌）+ ATR 波動率過濾。
與 INDA-002 的差異：以 2日急跌替代 10日高點回檔深度過濾，
捕捉短期動量崩潰而非從高點回落的訊號。

Att1: RSI(2)<10 + ATR>1.15 + ClosePos≥40%
  → Part A -0.61 / Part B -0.05（RSI(2) 無深度確認，進入結構性下跌）
Att2: WR(10)≤-80 + 2日跌幅≤-1.5% + ATR>1.15 + 冷卻10天
  → Part A 0.13 / Part B 0.13（A/B 平衡優秀但訊號太多，品質被稀釋）
Att3: WR(10)≤-80 + 2日跌幅≤-2.0% + ClosePos≥40% + ATR>1.15 + 冷卻10天
  → 更嚴格 2日跌幅 + 加回 ClosePos 反轉確認，提升選擇性
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDAMomentumCrashConfig(ExperimentConfig):
    """INDA 短期動量崩潰均值回歸參數"""

    # Williams %R 超賣確認
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # >= 40%

    # 2日急跌過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.02  # 2日跌幅 ≥ 2.0%（Att3 更嚴格）

    # 波動率自適應過濾
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期
    cooldown_days: int = 10  # 比 INDA-002 的 7 天更長，防止危機連續訊號


def create_default_config() -> INDAMomentumCrashConfig:
    return INDAMomentumCrashConfig(
        name="inda_004_rsi2_atr_adaptive",
        experiment_id="INDA-004",
        display_name="INDA Momentum Crash Mean Reversion",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=20,
    )
