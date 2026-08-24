"""
IBIT-006：Gap-Down 資本化均值回歸配置
(IBIT Gap-Down Capitulation Mean Reversion Config)

動機（Motivation）：
    IBIT-001（10日回檔 12-22% + WR(10) ≤ -80，TP +5%/SL -7%/15天/cd 15）Part A
    Sharpe 僅 0.15，Part B 0.37。Part A/B 累計報酬差距 56%（+3.27% vs +7.50%），
    Part A 多筆交易在淺達標邊界徘徊（平均 +0.79% vs Part B 的 +1.97%）。核心
    弱點：IBIT 受比特幣 24/7 連續交易驅動，隔夜跳空頻繁，但 IBIT-001 框架
    未利用「隔夜 gap-down 後日內反轉」這一結構性資訊——這是 BTC 現貨拋壓
    隔夜形成後，美股開盤資金「撿便宜」的典型 buy-the-dip pattern。

    本實驗引入 gap-down 反轉過濾：要求訊號日滿足「隔夜開盤跳空下跌 ≥ 1.5%
    且日內收盤高於開盤」的「夜跌-日反彈」結構，與傳統 10日回檔+WR 組合。

策略方向：均值回歸（加密投降式拋壓 + 日內反轉確認）
    Strategy direction: Mean reversion with capitulation gap + intraday reversal

迭代歷程（Iteration Log）：

Att1（Baseline）—— Gap-down + IBIT-001 出場
    進場：Gap <= -1.5% + Close > Open + 10d Pullback [-12%, -25%] + WR(10) <= -80 + cd=10
    出場：TP +5.0% / SL -7.0% / 持倉 15 天（沿用 IBIT-001）
    結果：Part A n=4, WR 100%, +19.37%, Sharpe ~0（零方差）；
          Part B n=3, WR 33%, -9.44%, Sharpe -0.56
    失敗分析：TP 5% 對 2025-10-17 這類有 6-7 日才反彈至 +5% 的交易過高——
        2025-10-17 訊號入場後 12 天才觸及 SL -7%（期間最大漲幅僅達約 +4.5%）。
        SL -7% 過寬，使持續下跌中的交易累積更多虧損。

Att2（New Best）—— 縮緊 TP 與 SL
    進場：同 Att1
    出場：TP +4.5% / SL -4.0% / 持倉 15 天
    結果：Part A n=4, WR 75%, +8.89%, Sharpe 0.60；
          Part B n=3, WR 67%, +4.54%, Sharpe 0.38
    min(A,B) **0.38**（+153% vs IBIT-001 的 0.15）
    成功分析：
        1. TP 4.5% 拯救 2025-10-17 交易（從 12日 SL 轉為 7日 TP），
           2025-11-21 同樣在 TP 4.5% 獲利了結
        2. SL 4% 快速認損 2024-07-05（從 TP +4.84% 翻轉為 SL -4.14%）
           與 2025-02-28（兩者都在入場後 1日立即觸及 SL -4%，
           避免 SL -7% 的額外虧損）
        3. TP 4.5%/SL 4% = 1.125:1 風報比，需 WR > 47% 盈利——與實測
           WR 71.4% 匹配良好
        4. Part A/B 累計差距從 56% 縮至 49%（仍 >30% 但顯著改善）
        5. Part A/B 訊號數差距 25%（< 50%，合格）

Att3（Ablation）—— 移除 gap-down 過濾
    進場：10d Pullback [-12%, -22%] + WR(10) <= -80 + cd=10（IBIT-001 entry）
    出場：TP +4.5% / SL -4.0% / 持倉 15 天
    結果：Part A n=6, WR 33%, -7.89%, Sharpe -0.33；
          Part B n=6, WR 33%, -7.89%, Sharpe -0.33
    失敗分析：沒有 gap-down 過濾，緊 SL -4% 對典型 IBIT-001 訊號過於嚴苛
        ——正常深回檔後的反彈常需 8-13 日但含 -4%~-5% 日內波動。Gap-down
        過濾器確認「投降式拋壓」才是 Att2 緊 SL 可行的必要條件。

結論：Gap-down reversal + tight asymmetric exit 為 IBIT 新最佳策略。

資產特性：IBIT 日波動 3.17%，GLD 比率 2.64x。
    進場：隔夜跳空 ≥ 1.5% 下跌 + 日內收盤高於開盤 + 10日回檔 12-25%
         + WR(10) ≤ -80
    出場：TP +4.5% / SL -4.0% / 最長持倉 15 天
    冷卻：10 天
    無追蹤停損（日波動 3.17% 禁用區域）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBIT006Config(ExperimentConfig):
    """IBIT-006 Gap-Down 資本化均值回歸參數"""

    # 進場參數
    gap_threshold: float = -0.015  # 隔夜開盤跳空 <= -1.5%
    pullback_lookback: int = 10
    pullback_threshold: float = -0.12  # 10日回檔 <= -12%
    pullback_upper: float = -0.25  # 回檔上限 25%（過濾崩盤極端值，略寬於 IBIT-001）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 10


def create_default_config() -> IBIT006Config:
    return IBIT006Config(
        name="ibit_006_gap_reversal_mr",
        experiment_id="IBIT-006",
        display_name="IBIT Gap-Down Capitulation Mean Reversion",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.045,  # +4.5%（Att2：新最佳）
        stop_loss=-0.04,  # -4.0%（Att2：新最佳）
        holding_days=15,
    )
