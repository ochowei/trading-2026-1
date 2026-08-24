"""
EEM-006: RS Momentum Pullback 配置
EEM Relative Strength Momentum Pullback Configuration

策略概念：當 EEM 相對 SPY 展現超額表現（EM 優於 DM），
在短期回調時買入，捕捉 EM 資金流動量。

參考 TSM-008（Sharpe 0.79）和 SOXL-010（Sharpe 0.70）的
RS 動量框架，按 EEM 波動度（1.17%）調整參數。

設計理據：
- RS 動量在 repo 中僅 SOXL/TSM 使用，均獲極高 Sharpe
- EEM vs SPY RS 捕捉 EM/DM 宏觀週期（risk-on/risk-off）
- 與均值回歸不同，不在危機中買入（避開 EEM-001~003 的 Part A 失敗）
- 與 BB Squeeze 不同，有基本面支撐（EM 超額表現週期）

三次嘗試結果：
- Att1: RS(20d)>=3% + Pullback 2-4% + SMA(50) + TP3.0%/SL3.0%/20d + cd10
  Part A 0.34 (9sig, WR 66.7%), Part B -0.23 (5sig, WR 40.0%)
  Part B 3 筆虧損：1 慢漂移到期、2 關稅衝擊停損

- Att2: RS(10d)>=2% + Pullback 2-6% + SMA(50) + TP3.0%/SL3.0%/20d + cd10
  Part A -0.13 (9sig, WR 44.4%), Part B -0.38 (3sig, WR 33.3%)
  10日 RS 太噪，新增 3 筆 Part A 停損

- Att3: RS(20d)>=3.5% + Pullback 2-5% + SMA金叉 + TP3.0%/SL3.0%/20d + cd10
  Part A 0.87 (6sig, WR 83.3%), Part B -0.60 (4sig, WR 25.0%)
  金叉過濾 Part A 噪音但移除 Part B 好訊號，A/B 差距擴大

結論：RS 動量不適用 EEM。EEM-SPY 相對強度由不可預測的宏觀/政治事件驅動
（關稅、貿易戰、中國政策），非結構性因素。確認跨資產教訓 #20。
最終保留 Att1 參數（最小過擬合）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEMRSMomentumConfig(ExperimentConfig):
    """EEM RS Momentum Pullback 策略專屬參數"""

    reference_ticker: str = "SPY"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.03
    pullback_lookback: int = 5
    pullback_min: float = 0.02
    pullback_max: float = 0.04
    cooldown_days: int = 10


def create_default_config() -> EEMRSMomentumConfig:
    return EEMRSMomentumConfig(
        name="eem_006_rs_momentum_pullback",
        experiment_id="EEM-006",
        display_name="EEM RS Momentum Pullback",
        tickers=["EEM"],
        data_start="2018-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
