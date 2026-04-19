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

    Att2（加嚴）：加深 capitulation 門檻 → pullback ≥ -4%、WR ≤ -90、2DD ≤ -2.5%
      並要求反轉擴張 Range[T] ≥ avg(Range[T-5..T-1]) × 1.2。假說：更極端超賣
      搭配擴張反轉可濾除中度下跌的假反彈，只留下真正崩盤後的 V 型反彈
      結果：Part A 3 訊號 WR 66.7% Sharpe 0.16；**Part B 0 訊號**（過嚴）。確認
      WR≤-90 + 2DD≤-2.5% + 1.2x range 三重加嚴在 TLT 1.0% vol 下過於稀少

    Att3（折衷）：維持 Att1 的 pullback -3%/-8%、WR ≤ -85，但加深 2DD 至 -2.0%
      並要求適度擴張 Range[T] ≥ avg(Range) × 1.15，冷卻延長至 10 天。目標：
      在保留 Part B 訊號的前提下，提升 Part A 的訊號品質
      結果：Part A 5 訊號 WR 40% Sharpe -0.39；**Part B 0 訊號**。Range 1.15x
      過濾對 TLT 1.0% vol 仍過嚴（日均 range 約 1.2-1.5%，要求 > 1.38% 擴張）
      且殘存 Part A 訊號集中於 2022-2023 高利率期間，反彈品質低

    結論（3 次迭代均失敗，擴展 lesson 20b / URA-009 邊界）：
      Day-After Capitulation + 強反轉 K 線模式在 TLT 上完全失敗，與 URA-009
      屬於同一失敗範式——「政策/事件驅動資產的單日/雙日反轉確認無法區分真實
      反轉 vs 暫時回彈」。具體失敗點：
      - Att1 顯示 2022-2023 升息期間「Close > Prev High」屢次出現但後續持續
        下跌（8/15 停損集中於該期間）
      - Att2/Att3 收緊後 Part B 立即枯竭，TLT 2024-2025 高利率高原期缺乏足夠的
        capitulation → reversal 事件支撐樣本
      - TLT 反轉強度受聯準會政策預期主導，技術面 price-action 過濾器無法
        作為有效的 regime 切換指標
      確認 TLT 的「無純技術面解法」結論（EXPERIMENTS_TLT.md 與 cross_asset
      lesson #30）擴展至 Day-After Capitulation 結構
    """

    # T-1 capitulation 評估（針對前一日）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 昨日回檔 ≥ 3%（Att3 回到 Att1）
    pullback_upper: float = -0.08  # 昨日回檔 ≤ 8%
    wr_period: int = 10
    wr_threshold: float = -85.0  # 昨日 WR(10) ≤ -85（Att3 回到 Att1）
    two_day_decline: float = -0.020  # T-3→T-1 兩日跌幅 ≤ -2.0%（Att3 折衷）

    # T 反轉強度：收復昨日高點 + 陽線 + 擴張 K 線
    require_prev_high_reclaim: bool = True  # Close > Prev High
    require_range_expansion: bool = True  # Range[T] ≥ avg range × 倍率
    range_expansion_ratio: float = 1.15  # Att3 折衷（Att1 無、Att2 1.2）
    range_expansion_lookback: int = 5  # 參考過去 N 日平均 range

    cooldown_days: int = 10  # Att3 延長（Att1/2 7）


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
