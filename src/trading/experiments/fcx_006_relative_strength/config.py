"""
FCX-006: Relative Strength 配置
FCX Relative Strength (FCX vs COPX) Configuration

策略邏輯（inspired by TSM-008）：
- 進場：FCX 20日報酬 - COPX 20日報酬 >= 5%（FCX 相對銅礦板塊超額表現）
       + 5日高點回撤 3-7%（短暫整理提供進場機會）
       + Close > SMA(50)（上升趨勢確認）
       + 冷卻期 10 個交易日
- 出場：TP +8% / SL -7% / 25天（沿用 TSM-008 最佳出場參數）

三次嘗試結果（全部失敗）：
- Att1: RS>=5%, pullback 3-7% → Part A 0.20 / Part B -0.15（5訊號，A/B比6:1嚴重不平衡）
- Att2: RS>=8%, pullback 3-8% → Part A -0.10 / Part B 無訊號（門檻過高殺死所有OOS訊號）
- Att3: RS>=3%, pullback 3-8% → Part A 0.18 / Part B -0.19（9訊號，WR僅33.3%，MDD -20.94%）

結論：FCX-COPX 相對強度在 2020 銅礦復甦期集中爆發（FCX 大幅超越 COPX），
但 2024-2025 兩者高度同步，RS 訊號在 OOS 期間無預測力。
與 TSM-SMH RS 不同，FCX-COPX 缺乏持續性的個股超額表現驅動因素。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXRelativeStrengthConfig(ExperimentConfig):
    """FCX Relative Strength 策略專屬參數"""

    reference_ticker: str = "COPX"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10


def create_default_config() -> FCXRelativeStrengthConfig:
    return FCXRelativeStrengthConfig(
        name="fcx_006_relative_strength",
        experiment_id="FCX-006",
        display_name="FCX Relative Strength (FCX vs COPX)",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
