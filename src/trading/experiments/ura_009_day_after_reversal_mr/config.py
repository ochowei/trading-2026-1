"""
URA Day-After Capitulation Mean Reversion 配置 (URA-009)

實驗動機：URA-008 RSI(14) bullish hook divergence 在 URA 上失敗，根因在於
URA 為核能政策/鈾價供應衝擊驅動，RSI 轉折常為 V-bounce 後繼續深跌（2025-11-05 訊號
隔日直接跌穿 SL 為典型）。URA-008 Att3 Part B WR 僅 33.3%。

本實驗不用任何振盪器轉折作為確認，改採「日後進場 + 單根反彈K線」的時間緩衝：
在捕捉到「昨日為極端 capitulation」之後，等待「今日為明確的反轉K線」才進場。
反轉 K 線定義需同時滿足 Close > 昨日 Close（收盤向上）且 Close > 今日 Open（陽線）。
藉由額外的一日等待與兩重 bar-level 確認，過濾掉假 V-bounce 並放棄一部分速度。

設計理念（三次迭代計畫）：
  Att1：昨日 pullback 10-20% + WR(10)≤-85 + 2DD(T-3→T-1)≤-4% + 今日反彈 K 線
  Att2：根據 Att1 結果調整閾值（WR, 2DD, pullback 深度）
  Att3：根據 Att1/Att2 結果微調出場參數

與既有 URA 實驗的差異：
- URA-001/002/004：進場點落在 capitulation 當日（RSI/WR 觸發即進）
- URA-008：依賴 RSI(14) hook 單一振盪器確認
- URA-009：依賴 price-action bar confirmation（close-vs-prev-close + close-vs-open）
  且使用 T-1 為評估日、T 為進場評估日，結構上緩一天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URADayAfterReversalMRConfig(ExperimentConfig):
    """URA 日後資本化 + 單K反轉 均值回歸參數"""

    # 進場指標（針對 T-1 評估）
    pullback_lookback: int = 10  # 10日回看
    pullback_threshold: float = -0.10  # 昨日回檔 ≥ 10%
    pullback_upper: float = -0.20  # 昨日回檔 ≤ 20%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # 昨日 WR(10) ≤ -80（同 URA-004 進場，Att3 放寬）
    two_day_decline: float = -0.03  # 從 T-3 到 T-1 兩日跌幅 ≤ -3%（同 URA-004，Att3 放寬）
    cooldown_days: int = 10

    # 反轉強度要求（Att2）：今日收盤收復昨日 High，比 Att1 單純 Close>Open 更嚴格
    # 提供真正的反轉強度過濾，排除「僅微幅反彈」的假訊號
    require_prev_high_reclaim: bool = True


def create_default_config() -> URADayAfterReversalMRConfig:
    return URADayAfterReversalMRConfig(
        name="ura_009_day_after_reversal_mr",
        experiment_id="URA-009",
        display_name="URA Day-After Capitulation MR",
        tickers=["URA"],
        data_start="2010-11-05",
        profit_target=0.060,  # +6.0%（同 URA-004）
        stop_loss=-0.055,  # -5.5%（同 URA-004）
        holding_days=20,
    )
