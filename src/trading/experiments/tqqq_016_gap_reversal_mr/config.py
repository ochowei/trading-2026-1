"""
TQQQ-016：Gap-Down 資本化 + 日內反轉均值回歸配置（3 次迭代全部失敗）
(TQQQ Gap-Down Capitulation + Intraday Reversal MR Config — All 3 attempts failed)

動機（Motivation）：
    TQQQ-010（20日回撤 <= -15% + RSI(5)<25 + Volume > 1.5x SMA20，TP+7%/SL-8%/10d）
    Part A Sharpe 0.36（20訊號, WR 70%, 累計 +55.44%），Part B Sharpe 1.02
    （8訊號, WR 87.5%, 累計 +47.59%）。min(A,B) = 0.36。
    Part A Sharpe 被兩筆 2020 崩盤初期停損重挫（2020-02-24 max_dd -11.1%,
    2020-03-12 max_dd -29.26%），std_return 達 6.92% 拖累 Sharpe，儘管 WR 70%。

    QQQ 盤後因美股科技七雄（AAPL/MSFT/NVDA/GOOGL/AMZN/META）財報、Fed/CPI
    早盤 8:30 ET 公告、亞/歐市場聯動產生顯著隔夜跳空，3x 槓桿 TQQQ 會放大這些
    gap 至 3 倍。本實驗借鏡 IBIT-006（+167% vs IBIT-001），驗證 lesson #20a
    (cross_asset_lessons.md)「Gap-Down 資本化 + 日內反轉」模式是否延伸至 3x
    槓桿科技 ETF。

策略方向：均值回歸（槓桿科技 ETF 投降式拋壓 + 日內反轉確認）

迭代歷程（Iteration Log）：

Att1（baseline）—— 深 gap 門檻
    進場：20d DD <= -15% + RSI(5) < 25 + Gap <= -3.0% + Close > Open + cd 10
    出場：TP +7% / SL -8% / 持倉 10 天（沿用 TQQQ-010）
    結果：Part A n=3, WR 100%, +22.50%, Sharpe 0.00（零方差 3/3 全贏 +7%）
          Part B n=2, WR 50%, -1.66%, Sharpe -0.07
    min(A,B) -0.07（vs TQQQ-010 的 0.36，-119%）
    失敗分析：-3% gap 相對 TQQQ 日波動 5-6% 為 0.55σ，門檻過嚴。
        Part A 僅捕捉 2020-02-28、2022-01-10、2022-05-12 三筆訊號，
        過濾掉 TQQQ-010 多數有效訊號（含 2020-03-12 深 gap 停損）。
        Part B 極低頻（1.0/年），統計意義不足。

Att2（loosen gap threshold）—— 將 gap 門檻放寬至 -2%
    進場：20d DD <= -15% + RSI(5) < 25 + Gap <= -2.0% + Close > Open + cd 10
         （移除 volume filter 以測試 gap 獨立過濾力）
    出場：同 Att1
    結果：Part A n=5, WR 60%, +3.48%, Sharpe 0.13
          Part B n=2, WR 50%, -1.66%, Sharpe -0.07
    min(A,B) -0.07（無改善）
    失敗分析：放寬至 -2% 新增 2022-09-01 及 2023-08-11 兩筆訊號，
        兩筆皆為「gap-down + 日內反轉」但非真正投降式——
        2022-09-01 Labor Day 前夕假反彈、2023-08-11 AI 泡沫回撤初期。
        兩筆均停損 -8.09%。WR 自 100%→60%，Sharpe 暴跌。
        Part B 訊號不變（2024-08-05 勝、2025-04-07 敗）。

Att3（+ volume filter, 複製 TQQQ-010 baseline）—— 加回 volume 過濾
    進場：20d DD <= -15% + RSI(5) < 25 + Volume > 1.5x SMA(20) + Gap <= -2.0%
         + Close > Open + cd 10
    出場：同 Att1
    結果：Part A n=4, WR 75%, +12.59%, Sharpe 0.49
          Part B n=2, WR 50%, -1.66%, Sharpe -0.07
    min(A,B) -0.07（vs TQQQ-010 的 0.36，無改善）
    失敗分析：Volume filter 移除 2023-08-11 訊號（非 volume 飆升日），
        Part A Sharpe 改善至 0.49。但 Part B 完全不變（兩筆皆 volume 飆升）。
        核心失敗：**Part B 2025-04-07（Trump 關稅公告後）屬「gap-down + 日內反彈」
        結構但隔日繼續深跌**，觸發 -8% 停損。

結論與教訓：
    1. **Gap-Down 反轉模式不延伸至 3x 槓桿科技 ETF**：
       與 IBIT 24/7 連續交易不同，QQQ 盤外交易量有限，盤中 gap-down 常反映
       盤前事件（Fed/CPI/科技巨頭財報）而非投降式拋壓。若事件基本面利空持續，
       日內反轉只是技術反彈而非底部。
    2. **TQQQ 在 2024-2025 樣本過稀**：大牛市期 gap-down 事件僅 2 筆（2024-08-05
       yen carry unwind、2025-04-07 關稅），統計信心不足。
    3. **Volume filter 對 Part A 仍有效**：移除 2023-08-11 假反彈提升 Sharpe
       0.13→0.49，但 Part B 無改善。
    4. **Lesson #20a 更新**：Gap-Down 資本化模式確認**不適用於傳統（非 24/7）
       標的之槓桿 ETF**。適用邊界：加密 ETF（IBIT 驗證）；不適用：TQQQ（3x 科技）。

資產特性：TQQQ 日波動 5-6%，GLD 比率 ~4.5x。Att3 為本實驗最佳但仍落後 TQQQ-010。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQ016Config(ExperimentConfig):
    """TQQQ-016 Gap-Down 資本化均值回歸參數（Att3 最終版，全實驗失敗）"""

    # 進場參數
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.15
    rsi_period: int = 5
    rsi_threshold: float = 25.0
    gap_threshold: float = -0.02  # Att3 最終版：-2%
    volume_multiplier: float = 1.5  # Att3 加回 volume 過濾
    volume_sma_period: int = 20
    cooldown_days: int = 10


def create_default_config() -> TQQQ016Config:
    return TQQQ016Config(
        name="tqqq_016_gap_reversal_mr",
        experiment_id="TQQQ-016",
        display_name="TQQQ Gap-Down Capitulation + Intraday Reversal MR",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,
        stop_loss=-0.08,
        holding_days=10,
    )
