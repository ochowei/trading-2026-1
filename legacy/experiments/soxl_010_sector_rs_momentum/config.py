"""
SOXL-010: Semiconductor Sector RS Momentum Pullback 配置

半導體板塊相對強度動量策略：在 SOXX 相對 SPY 顯示強勢時，買入 SOXL 短期回調。
- SOXX 10日報酬 - SPY 10日報酬 >= 6%（半導體板塊跑贏大盤，短期動量）
- SOXL 5日高點回撤 8-16%（槓桿 ETF 短暫整理，非深度回調）
- SOXL Close > SMA(50)（上升趨勢確認）
- 冷卻期 10 天

三次嘗試：
- Att1: RS(20d) >= 8%, pullback 8-16%, TP+15%/SL-12%/20d/cd10 → Part A 0.70/B 0.11（RS 太嚴,20d 回看捕捉動量尾端）
- Att2: RS(20d) >= 5%, pullback 6-15%, TP+18%/SL-12%/25d/cd15 → Part A 0.38/B -0.35（RS 太鬆，大量壞訊號）
- Att3: RS(10d) >= 6%, pullback 8-16%, TP+15%/SL-12%/20d/cd10 → 本次（10日回看偵測早期動量）

與 SOXL-006 差異：SOXL-006 使用極端超賣進場（-25%~-40% 回撤），本策略使用
板塊相對強度動量，在上漲趨勢中買入回調。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLSectorRSConfig(ExperimentConfig):
    """SOXL 半導體板塊 RS 動量策略專屬參數"""

    # 多標的參數 (Multi-asset parameters)
    sector_ticker: str = "SOXX"
    benchmark_ticker: str = "SPY"

    # 相對強度參數 (Relative strength parameters)
    relative_strength_period: int = 10
    relative_strength_min: float = 0.06

    # 回調參數 (Pullback parameters)
    pullback_lookback: int = 5
    pullback_min: float = 0.08
    pullback_max: float = 0.16

    # 趨勢確認 (Trend confirmation)
    sma_trend_period: int = 50

    # 冷卻期 (Cooldown)
    cooldown_days: int = 10

    # 成交模型 (Execution model)
    slippage_pct: float = 0.001


def create_default_config() -> SOXLSectorRSConfig:
    return SOXLSectorRSConfig(
        name="soxl_010_sector_rs_momentum",
        experiment_id="SOXL-010",
        display_name="SOXL Semiconductor Sector RS Momentum Pullback",
        tickers=["SOXL"],
        data_start="2018-01-01",
        profit_target=0.15,
        stop_loss=-0.12,
        holding_days=20,
    )
