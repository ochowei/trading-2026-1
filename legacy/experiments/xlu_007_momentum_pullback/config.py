"""
XLU-007: XLU/SPY Pairs Trading 配置
XLU-SPY Pairs Trading Configuration

假說：XLU/SPY 比值反映防禦性輪動週期。當 XLU 相對 SPY 顯著落後
（z-score < -1.5），預期輪動資金回流 XLU，做多 XLU。
SMA(50) 確保 XLU 長期趨勢向上（非結構性崩潰如 2022 升息）。

=== 三次嘗試記錄 ===

Attempt 1: 動量回檔（ROC(20)>3% + 5日回檔<-1.5% + SMA(50)）
  TP+3.0%/SL-4.0%/20天，冷卻10天
  結果：Part A Sharpe -0.33（WR 38.5%），Part B -0.81（WR 20.0%）
  分析：XLU 的回檔在上升趨勢中往往持續擴大（利率敏感），
  動量回檔策略不適用公用事業 ETF。

Attempt 2（當前版本）: XLU/SPY 配對交易（z-score(40) < -1.5 + SMA(50)）
  TP+2.5%/SL-4.0%/20天，冷卻10天
  結果：Part A Sharpe 0.08（WR 55.6%，18訊號），Part B Sharpe 0.67（WR 85.7%，7訊號）
  分析：Part B 優異但 Part A 太弱。2020-2021 風險偏好期 XLU 持續落後 SPY
  （非超賣，純結構性輪出），z-score 訊號品質低。min(A,B) = 0.08 < XLU-004 的 0.18。

Attempt 3: XLU/SPY 配對 + WR(10)≤-80 超賣確認（z-score < -2.0）
  TP+2.5%/SL-4.0%/20天，冷卻10天
  結果：Part A Sharpe 0.48（WR 75%，4訊號），Part B 僅 1 訊號不可評估
  分析：條件過嚴，訊號過少。A/B 比 4:1 不合格。

結論：三次嘗試均未超越 XLU-004（min(A,B) 0.18）。XLU/SPY 配對交易的根本問題
是 XLU 在 2020-2021 風險偏好期持續相對落後（結構性非週期性），
z-score 均值回歸假設在該時期不成立。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU007Config(ExperimentConfig):
    """XLU-007 XLU/SPY Pairs Trading 策略專屬參數"""

    # Pairs trading 參數
    zscore_lookback: int = 40
    zscore_threshold: float = -1.5

    # 趨勢確認
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> XLU007Config:
    """建立預設配置"""
    return XLU007Config(
        name="xlu_007_momentum_pullback",
        experiment_id="XLU-007",
        display_name="XLU-SPY Pairs Trading",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,
        stop_loss=-0.04,
        holding_days=20,
    )
