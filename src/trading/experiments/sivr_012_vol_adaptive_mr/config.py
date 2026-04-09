"""
SIVR-012: Volatility-Adaptive Mean Reversion
(SIVR 波動率自適應均值回歸)

基於 SIVR-005（回檔 7-15% + WR(10) ≤ -80），新增 ATR(5)/ATR(20) 波動率
飆升過濾器，區分急跌回檔（有效均值回歸）與緩慢下漂（低品質訊號）。

靈感來自 XLU-011 的成功（min(A,B) Sharpe +272%），將同一概念移植到
波動度更高的 SIVR（日波動 2-3% vs XLU ~1.0-1.5%）。

Att1（最終選擇）: ATR > 1.15, SL -3.5% → Part A Sharpe 0.41 / Part B 0.12
  Part A 大幅改善（+86% vs SIVR-005），但 Part B 3 個好訊號被過濾掉
Att2: ATR > 1.10, SL -3.5% → Part A 0.08 / Part B -0.02
  較寬鬆門檻引入 Part A 3 個壞訊號（WR 70%→56.5%）
Att3: ATR > 1.15, SL -4.0% → Part A 0.34 / Part B 0.06
  寬 SL 未能挽救任何 Part B 停損（跌幅遠超 -4%），反增大每筆虧損

結論：ATR 過濾器在 Part A 表現卓越但 Part B 退化，
波動率飆升過濾在日波動 2-3% 的資產上無法跨期穩定。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRVolAdaptiveMRConfig(ExperimentConfig):
    """SIVR 波動率自適應均值回歸參數"""

    # 回檔參數（同 SIVR-005）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 >= 7%
    pullback_cap: float = -0.15  # 回檔 <= 15%

    # Williams %R 參數（同 SIVR-005）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期（同 SIVR-005）
    cooldown_days: int = 10


def create_default_config() -> SIVRVolAdaptiveMRConfig:
    return SIVRVolAdaptiveMRConfig(
        name="sivr_012_vol_adaptive_mr",
        experiment_id="SIVR-012",
        display_name="SIVR Volatility-Adaptive Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（SIVR 甜蜜點）
        stop_loss=-0.035,  # -3.5%（SIVR 甜蜜點）
        holding_days=15,
    )
