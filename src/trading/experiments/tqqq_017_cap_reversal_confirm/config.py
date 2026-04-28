"""
TQQQ-017：恐慌抄底 + 盤中/加速確認 (Capitulation + Intraday/Acceleration Confirmation)

動機（Motivation）：
    TQQQ-010（當前最佳）在 Part A 出現 6 筆停損（20 訊號中，WR 70%，
    Sharpe 0.36），拖累 min(A,B) 從 Part B 的 1.02 降至 0.36。
    Part A 停損日期：2020-02-24、2020-03-12、2021-09-28、2022-03-08、
    2022-09-01、2022-09-21。觀察這些日子的共同特徵與勝利日的差異，設計
    篩選器以過濾「持續性下跌中的偽訊號」但保留「急速恐慌後的真反轉」。

策略方向：均值回歸（加入日內/加速/多日確認過濾）

迭代歷程（Iteration Log）— 三次迭代全部失敗，TQQQ-010 仍為全域最優：

Att1 — ClosePos >= 0.30（日內反轉確認）【失敗】
    進場：20d DD <= -15% + RSI(5)<25 + Volume>1.5x SMA20 + ClosePos>=0.30
    結果：Part A n=11, WR 72.7%, Sharpe 0.43 (+19% vs TQQQ-010)
         Part B n=5, WR 60%, Sharpe 0.13 (-87% vs TQQQ-010)
    min(A,B) = 0.13（失敗，遠低於 TQQQ-010 的 0.36）
    失敗分析：
      - Part A 小幅改善因篩除部分 Part A 停損（2020-03-12、2021-09-28、
        2022-03-08、2022-09-21 四筆中篩除三筆）
      - 但 Part B 崩壞——ClosePos>=0.30 篩掉 TQQQ-010 原 7 個 Part B 勝者中 5 個
        （2024-04-19、2024-07-24、2024-09-06、2025-02-27、2025-04-04 均
        ClosePos<0.30），同時冷卻期偏移引入新壞訊號（2025-03-04 SL、2025-04-07 SL）
      - 核心問題：TQQQ 3x 槓桿 + 5-6% 日波動使恐慌日多收於當日低點附近
        （多數 TQQQ-010 勝者的 ClosePos < 30%），日內反轉發生於隔日而非當日。
        ClosePos 不僅篩除壞訊號也大量篩除好訊號，且在冷卻期內改變訊號日期
        （從勝利日偏移至次一可通過日）。**再度驗證 cross_asset_lesson #6
        （ClosePos 邊界 ≤ 2% vol）在 TQQQ 5-6% vol 上失效**

Att2 — 2 日加速跌幅 <= -10%（加速過濾）【失敗】
    進場：20d DD <= -15% + RSI(5)<25 + Volume>1.5x SMA20 + Return2D<=-0.10
    結果：Part A n=10, WR 60%, Sharpe 0.13
         Part B n=4, WR 75%, Sharpe 0.49
    min(A,B) = 0.13（失敗）
    失敗分析：
      - 2-day -10% 過濾器移除 Part A 原 20 訊號中的 10 筆，保留結構：
        6W/4L（vs TQQQ-010 的 14W/6L），WR 從 70% 降至 60%
      - 篩除 8 個勝者（2019-10-02、2021-02-25、2021-05-12、2021-10-04、
        2022-01-10、2022-04-26、2022-05-11、2023-09-27）與 2 個敗者
        （2022-09-01、2022-09-21）——**篩除比例「壞」於整體**（80%勝者 vs 33%敗者）
      - Part B 8→4 訊號，雖 WR 75% 但訊號數減半且 Sharpe 0.49 遠低於 TQQQ-010 1.02
      - **核心問題**：TQQQ 勝者訊號並非皆伴隨極端 2 日急跌；多數是「中等 2 日下跌
        疊加既有 DD」的訊號（如 2021-02-25 Fed pivot、2022-01-10 科技財報擔憂）。
        強制 2 日 -10% 門檻反而移除這些高品質中等加速訊號。確認「加速度」
        不是 TQQQ 贏/輸的關鍵區分軸

Att3 — Prev RSI(5) < 30（前日超賣確認）【最接近基線但仍未超越】
    進場：20d DD <= -15% + RSI(5)<25 + Volume>1.5x SMA20 + Prev RSI(5)<30
    結果：Part A n=13, WR 69.2%, Sharpe **0.34** (vs TQQQ-010 的 0.36，-0.02)
         Part B n=8, WR 87.5%, Sharpe **1.02** (與 TQQQ-010 完全相同)
    min(A,B) = 0.34（vs TQQQ-010 的 0.36，-0.02 邊際劣化）
    失敗分析：
      - Part B 與 TQQQ-010 表現**完全相同**（Sharpe 1.02、WR 87.5%、cum +47.59%），
        確認 Part B 所有 8 筆 TQQQ-010 訊號之前一日 RSI(5) 皆 < 30（即「雙日超賣」
        條件天然成立於 Part B 訊號）
      - Part A 20→13 訊號，篩除 7 筆：4 勝者 + 2 敗者 + 1 冷卻偏移勝者
        （2019-10-02、2020-09-08、2021-02-25、2022-04-26 勝者被篩除；
        2022-09-01、2022-09-21 敗者被成功篩除；2021-09-28 敗者偏移至 2021-09-30 勝者）
      - 篩除比例大致相當（30% 敗者 vs 29% 勝者），無選擇性
      - 累計報酬從 +55.44% 降至 +31.19%（Sharpe 0.36→0.34），勝率 70%→69.2%
      - **核心問題**：Prev RSI<30 條件對 TQQQ 2019-2022 恐慌訊號「多半已天然成立」
        （持續性 2 日跌勢中 RSI(5) 在 T-1 日多已低於 30），過濾器僅移除少數「單日
        急跌至 RSI<25」訊號，其中既有勝者也有敗者

結論與教訓：
    1. **TQQQ-010 已達 Part A 結構性底線**：20 筆 Part A 訊號中的 6 筆停損
       無法用單日/雙日/多日技術過濾器可靠區分——停損訊號在 ClosePos、
       2DD、Prev RSI 等維度上與勝率訊號分布重疊
    2. **Part A Sharpe 0.36 天花板反映 3x 槓桿 ETF 的結構性噪音**：高波動
       標的在極端跌勢中即使「抄底成功」仍需承受 -8% SL 的機械觸發，
       Part A 包含 2020 COVID + 2022 科技熊市使 Part A std_return 達 6.92%
       拖累 Sharpe
    3. **Cross-asset lesson #6 在 TQQQ 再度驗證**：ClosePos 過濾器
       在日波動 > 2% 的資產上無效，TQQQ 5-6% 日波動遠超該邊界
    4. **Lesson #20b 失敗家族擴展至「加速/多日確認」過濾家族**：
       與 ClosePos（Att1）、2DD 加速（Att2）、Prev RSI（Att3）三類過濾器
       在 TQQQ 上均無法改善 min(A,B)，共同失敗模式為「過濾器移除的勝者/
       敗者比例不具選擇性」
    5. **TQQQ-010 確認為全域最優**（17 次實驗、累計含均值回歸、趨勢/動量/
       突破、Gap-Down 資本化、盤中/加速/多日確認五大策略類型均失敗於
       超越 TQQQ-010 的 min(A,B) 0.36）

最終配置（documenting Att3 as最接近基線之設計）：
    enable_two_day_filter=False（停用 Att2 2DD）
    close_position_threshold=0.0（停用 Att1 ClosePos）
    prev_rsi_threshold=30.0（保留 Att3 Prev RSI 作為預設展示）

資產特性：TQQQ 日波動 5-6%，GLD 比率 ~4.5x。
"""

from dataclasses import dataclass

from trading.experiments.tqqq_001_capitulation.config import TQQQConfig


@dataclass
class TQQQ017Config(TQQQConfig):
    """TQQQ-017：恐慌抄底 + 加速/確認過濾配置

    繼承 TQQQ-001 的三重進場條件，依迭代選擇加入不同過濾器。
    出場參數沿用 TQQQ-008/010 的優化值（TP +7% / SL -8% / 10 天持倉）。
    """

    # 沿用 TQQQ-001 核心參數（繼承預設）：
    #   drawdown_lookback: 20, drawdown_threshold: -0.15
    #   rsi_period: 5, rsi_threshold: 25.0
    #   volume_multiplier: 1.5, volume_sma_period: 20
    #   cooldown_days: 3

    # Att1（ClosePos 日內反轉，已驗證失敗）
    # close_position_threshold 保留為可選參數，<=0 表示停用該過濾器
    close_position_threshold: float = 0.0  # 0.0 = 停用（Att2/Att3 不使用）

    # Att2 新增：2 日加速跌幅過濾（已驗證失敗，保留以重現）
    two_day_return_threshold: float = -0.10
    enable_two_day_filter: bool = False  # Att3 停用

    # Att3：前一日 RSI(5) 超賣確認——要求「雙日超賣」以確認持續性恐慌
    # 過濾「今日單日急跌至 RSI<25」但昨日尚處正常區間的訊號
    prev_rsi_threshold: float = 30.0

    # 優化出場（同 TQQQ-008/010）
    profit_target: float = 0.07
    stop_loss: float = -0.08
    holding_days: int = 10

    # 成交模型
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ017Config:
    return TQQQ017Config(
        name="tqqq_017_cap_reversal_confirm",
        experiment_id="TQQQ-017",
        display_name="TQQQ Capitulation + Acceleration/Recovery Confirmation",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
    )
