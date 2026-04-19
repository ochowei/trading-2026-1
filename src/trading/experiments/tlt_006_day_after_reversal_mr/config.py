"""
TLT Day-After Capitulation Mean Reversion 配置 (TLT-006)

實驗動機：TLT-002 為當前最佳（Part A Sharpe -0.20，Part B Sharpe 0.24），Part A 被
2022 升息週期連續假訊號殺死（32 訊號 WR 46.9%，累計 -16.83%）。TLT-004/005 的突破
策略在 Part A 有效（BB 擠壓 Sharpe 0.31、SMA 金叉 Sharpe 0.89）但 Part B 在橫盤
環境下災難性失敗（-1.15 ~ -1.43）。

URA-009 Att2 驗證「Day-After Capitulation + 強反轉 K 線」框架結構上能平衡 A/B
（0pp 累計差、60%/60% WR），但在 URA 核能政策驅動下 V-bounce 過多而失敗。TLT
同為宏觀政策驅動，但「收復昨日高點」的價格動作過濾器有結構性理由在 TLT 上有效：

- 2022 升息週期：Fed 鷹派訊息當日 TLT 大跌，隔日多為技術性小反彈但極少收復前日 High
  （持續性下跌週期 → 不斷創新低高點）。因此「Close > Prev High」天然過濾 Part A
  2022 整年假訊號
- 2024-2025 高利率高原期：Fed 政策預期穩定時 TLT 進入較正常的均值回歸，單日極端
  超賣後隔日反彈（若能收復前日 High）為真實回歸的高品質訊號
- Part B 的本質是「不在持續性 tightening 階段」，該環境中反彈多為真實（而非 V-bounce）

相較於 URA（核能政策週期短、V-bounce 頻繁），TLT 的反彈強度與政策前景高度相關，
「收復前高」為真正的 regime 轉換指標。

設計理念：
- T-1 為 capitulation 評估日（回檔深度+WR+2DD）
- T 為反轉確認日（Close > 昨日 High 且 Close > Open）
- T+1 開盤進場（由 execution model 負責）
- 出場沿用 TLT-002 驗證有效的 TP +2.5% / SL -3.5% / 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT006Config(ExperimentConfig):
    """TLT-006 Day-After Capitulation + 強反轉 K 線均值回歸參數

    Att1（基準嘗試）：pullback -3%/-8%、WR ≤ -85、2DD ≤ -1.5%、簡單 Close>PrevHigh 反轉
      結果：Part A -0.37（15 訊號 WR 40%）/ Part B 0.00（3 訊號 100% WR 零方差），
      min(A,B) -0.37（劣於 TLT-002 的 -0.20）。Close>PrevHigh 單項過濾不足以
      排除 2022-2023 持續升息期間的假訊號（8 次 -3.6% 停損集中於 2022 Aug-Sep
      與 2023 May-Sep）
    """

    # T-1 capitulation 評估（針對前一日）
    pullback_lookback: int = 10  # 10 日回看
    pullback_threshold: float = -0.03  # 昨日回檔 ≥ 3%（3σ for 1.0% vol）
    pullback_upper: float = -0.08  # 昨日回檔 ≤ 8%（8σ，過濾 2022 連續暴跌日）
    wr_period: int = 10
    wr_threshold: float = -85.0  # 昨日 WR(10) ≤ -85（極端超賣）
    two_day_decline: float = -0.015  # T-3→T-1 兩日跌幅 ≤ -1.5%

    # T 反轉強度：收盤收復昨日高點 + 陽線
    require_prev_high_reclaim: bool = True  # Close > Prev High

    cooldown_days: int = 7


def create_default_config() -> TLT006Config:
    return TLT006Config(
        name="tlt_006_day_after_reversal_mr",
        experiment_id="TLT-006",
        display_name="TLT Day-After Capitulation MR",
        tickers=["TLT"],
        data_start="2019-01-01",
        profit_target=0.025,  # +2.5%（同 TLT-002）
        stop_loss=-0.035,  # -3.5%（同 TLT-002）
        holding_days=20,
    )
