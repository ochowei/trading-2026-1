"""
COPX-006: COPX 短期均值回歸配置
COPX Short-Term Mean Reversion Configuration

Attempt 1（配對交易 COPX/FCX z-score）: Part A Sharpe -0.06, Part B -0.50 → 失敗
  原因：COPX/FCX 比率有結構性漂移，z-score 均值回歸不可靠，Part B 僅 3 訊號

Attempt 2（動量回檔 SMA50+RSI5+回檔）: Part A Sharpe -0.28, Part B 0.00 → 失敗
  原因：SMA(50) 趨勢濾波無法區分健康回檔 vs 趨勢反轉，Part A WR 40%，9 筆停損

Attempt 3（RSI(2) 短期均值回歸，模仿 URA-004）：
  假說：以 RSI(2) + 2日急跌 + 20日回檔作為進場條件，不加趨勢濾波器。
  與 COPX-003（WR+20日回檔 10-20%）不同的進場機制，與 COPX-002（RSI(2)<10+4%急跌）
  使用較寬鬆的門檻。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPXRsi2Config(ExperimentConfig):
    """COPX RSI(2) 短期均值回歸策略專屬參數"""

    rsi_period: int = 2
    rsi_threshold: float = 15.0
    two_day_decline_threshold: float = -0.03
    pullback_lookback: int = 20
    pullback_threshold: float = -0.05
    cooldown_days: int = 12


def create_default_config() -> COPXRsi2Config:
    """建立預設配置"""
    return COPXRsi2Config(
        name="copx_006_pairs_fcx",
        experiment_id="COPX-006",
        display_name="COPX RSI(2) Short-Term Mean Reversion",
        tickers=["COPX"],
        data_start="2018-01-01",
        profit_target=0.035,
        stop_loss=-0.045,
        holding_days=20,
    )
