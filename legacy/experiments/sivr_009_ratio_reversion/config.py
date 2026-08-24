"""
SIVR-009: Gold/Silver Ratio Mean Reversion 配置
(Gold/Silver Ratio Mean Reversion Configuration)

利用 GLD/SIVR 價格比率的 z-score 均值回歸特性。
當比率偏高（白銀相對黃金便宜）且 SIVR 處於超賣區間時買入。
這是一種配對交易/相對價值策略，不同於 SIVR-001~008 的絕對價格訊號。

Attempt 1: ratio z-score(60d) >= 1.5 + WR(10) <= -80, TP+3.5%/SL-3.5%/15d
  結果: Part A Sharpe 0.06 (23訊號, WR 52.2%), Part B Sharpe 0.64 (9訊號, WR 77.8%)
  問題: Part A 嚴重不足，2021-2023 比率結構性偏高產生大量假訊號

Attempt 2: ratio z-score(90d) >= 2.0 + WR(10) <= -80, TP+3.5%/SL-3.5%/15d
  結果: Part A Sharpe 0.22 (17訊號), Part B Sharpe 0.18 (5訊號)
  問題: z-score 2.0 太嚴格，Part B 訊號剩5個，A/B比 3.4:1

Attempt 3: ratio z-score(60d) >= 1.5 + 回檔 7-15% + WR(10) <= -80, TP+3.5%/SL-3.5%/15d
  結果: Part A Sharpe 0.18 (13訊號, WR 61.5%), Part B Sharpe 0.55 (4訊號, WR 75.0%)
  問題: min(A,B) 0.18 < SIVR-005 的 0.22，Part B 訊號僅 4 個（A/B 比 3.25:1）
  三次嘗試均未超越 SIVR-005。核心瓶頸：金銀比 2021-2023 結構性偏高產生 Part A 假訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRRatioReversionConfig(ExperimentConfig):
    """SIVR Gold/Silver Ratio Mean Reversion 參數"""

    # 比率 z-score 參數
    ratio_lookback: int = 60  # z-score 滾動窗口（交易日）
    ratio_zscore_threshold: float = 1.5  # z-score >= 1.5 表示白銀相對便宜

    # 絕對回檔範圍（過濾邊際訊號）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    pullback_cap: float = -0.15  # 回檔 ≤15%（過濾極端崩盤）

    # Williams %R 超賣確認
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 冷卻期
    cooldown_days: int = 10

    # 參考標的（用於計算比率，不交易）
    reference_ticker: str = "GLD"


def create_default_config() -> SIVRRatioReversionConfig:
    return SIVRRatioReversionConfig(
        name="sivr_009_ratio_reversion",
        experiment_id="SIVR-009",
        display_name="SIVR Gold/Silver Ratio Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,
    )
