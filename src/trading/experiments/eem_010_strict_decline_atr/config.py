"""
EEM-010: 嚴格跌幅 + ATR 波動率自適應 RSI(2)
(EEM Strict Decline + ATR Volatility-Adaptive RSI(2))

基於 EEM-009 分析，Part A 停損多來自 EM 危機初期淺跌訊號：
- 提高 2 日跌幅門檻至 2.0%（從 1.5%），要求更深恐慌才進場
- ATR 門檻降至 1.1（從 1.15），允許更多急跌訊號回流
- SL 維持 -3.5%，給予 EM 波動呼吸空間
- 此為 EEM-002 Att2(ATR>1.1+SL-3.5%) 和 EEM-003 Att1(decline 2.0%+ATR>1.15)
  的交叉組合，此精確組合尚未被測試過
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM010Config(ExperimentConfig):
    """EEM-010 嚴格跌幅 + ATR 自適應 RSI(2) 參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0

    # 2 日累計跌幅過濾（提高門檻）
    decline_lookback: int = 2
    decline_threshold: float = -0.020  # 2.0%（EEM-001~002 為 1.5%）

    # 收盤位置過濾
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（降低門檻）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.1  # 從 1.15 降至 1.1

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> EEM010Config:
    return EEM010Config(
        name="eem_010_strict_decline_atr",
        experiment_id="EEM-010",
        display_name="EEM Strict Decline + ATR RSI(2)",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=20,
    )
