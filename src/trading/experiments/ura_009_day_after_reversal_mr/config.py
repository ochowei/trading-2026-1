"""
URA Day-After Capitulation Mean Reversion 配置 (URA-009)

實驗動機：URA-008 RSI(14) bullish hook divergence 在 URA 上失敗，根因在於
URA 為核能政策/鈾價供應衝擊驅動，RSI 轉折常為 V-bounce 後繼續深跌（2025-11-05 訊號
隔日直接跌穿 SL 為典型）。URA-008 Att3 Part B WR 僅 33.3%。

本實驗不用任何振盪器轉折作為確認，改採「日後進場 + 單根反彈K線」的時間緩衝：
在捕捉到「昨日為極端 capitulation」之後，等待「今日為明確的反轉K線」才進場。
反轉 K 線定義需同時滿足 Close > 昨日 Close（收盤向上）且 Close > 今日 Open（陽線）。
藉由額外的一日等待與兩重 bar-level 確認，過濾掉假 V-bounce 並放棄一部分速度。

設計理念（三次迭代歷程）：
  Att1：WR(10)≤-85 + 2DD≤-4% + 反彈 K 線（Close>Prev Close, Close>Open）
    → Part A -0.25 / Part B 0.15，反轉過濾太弱
  Att2：同 Att1 + 強反轉過濾（Close > Prev High 收復昨日高點）
    → Part A/B 皆 0.24, WR 60%/60%，反轉過濾見效但訊號 ~1/yr 過稀
  Att3：放寬 T-1 至 WR≤-80, 2DD≤-3%（同 URA-004）+ 保留強反轉
    → Part A -0.08 / Part B -0.11，新增訊號 WR 崩至 43%

與既有 URA 實驗的差異：
- URA-001/002/004：進場點落在 capitulation 當日（RSI/WR 觸發即進）
- URA-008：依賴 RSI(14) hook 單一振盪器確認
- URA-009：依賴 price-action bar confirmation（close-vs-prev-close/high + close-vs-open）
  且使用 T-1 為評估日、T 為進場評估日，結構上緩一天

結論（3 次迭代全部失敗，URA-004 min(A,B) 0.39 仍為全域最優）：
  - 收復昨日高點（Close > Prev High）為強反轉過濾，Att2 單筆 WR 升至 60%
    但訊號年化僅 ~1 筆，樣本過薄
  - 放寬 capitulation 閾值無法在保留品質的前提下增加訊號，
    WR 立即崩至 43-44%
  - 與 URA-008 RSI hook 失敗同屬「V-bounce ≠ genuine reversal」
    範式：URA 核能政策/鈾價衝擊使任何「單日／雙日反轉」
    確認無法可靠區分暫時回彈 vs 真實反轉
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
