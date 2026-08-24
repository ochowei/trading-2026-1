"""
IBIT-008：單日 Range Expansion Climax 均值回歸配置
(IBIT Wide-Range Climax + Intraday Reversal Mean Reversion Config)

動機（Motivation）：
    IBIT-006 Att2（Gap-Down + 10日回檔 12-25% + WR(10)≤-80，TP+4.5%/SL-4%/15天）
    雖達 min(A,B) 0.40，但 Part A/B 累計差仍 66%（>30% 目標）且 Part B 僅 3 訊號
    （WR 67%, 累計 +4.68%）。核心限制：Gap-down ≤ -1.5% 過濾器依賴「隔夜跳空」
    結構，在 2025 年震盪期跳空幅度不足（BTC 盤外拋壓分散至盤中），產生過少訊號。
    IBIT-007 Keltner Lower MR 三次迭代全部失敗（min -0.31~0.00），證明波動率
    自適應「慢性超賣」偵測對高波動加密 ETF 無效。

    本實驗嘗試 **repo 首次單日 Range Expansion Climax** 作為主進場訊號：
        - 今日單日 True Range ≥ 2.0 × ATR(20)：單日波幅為近 20 日均值兩倍以上，
          代表賣壓/波動率的**爆發性 climax**（而非 NR7 的緩和收縮、也非 Keltner
          的長期偏離）
        - Close Position ≥ 50%：收盤價高於當日中點，確認日內買方在恐慌賣壓後
          接回主導權（強化版日內反轉，嚴於 Close > Open）
        - 10 日回檔 -6% ~ -20%：在下跌 regime 中捕捉 climax（避免牛市高點爆發
          範圍後的續跌）

    與現有 IBIT 實驗的結構差異：
        - IBIT-006（Gap-Down）：捕捉「隔夜拋壓完成」的 overnight 結構
        - IBIT-007（Keltner）：捕捉「EMA/ATR 靜態偏離」的慢性超賣
        - IBIT-008（Range Expansion）：捕捉「單日 TR 爆發」的當日 capitulation
          climax —— 既非隔夜也非長期偏離，而是「盤中的劇烈波動 + 日內反轉」

    與 cross-asset lesson #20a (Gap-Down)、lesson #15 (ATR 波動率自適應) 皆不同：
        - Lesson #20a 強調 overnight gap + intraday recovery（結構：盤外 → 盤中）
        - Lesson #15 的 ATR(5)/ATR(20) 比較**近期 vs 中期**波動率趨勢
        - 本實驗 TR / ATR(20) 比較**當日 vs 歷史**單點爆發

    Repo 首次將「Range Expansion（單日寬範圍 K 棒）作為 MR 主要觸發條件」的
    試驗（TLT-006 曾將 Range Expansion 作為多條件之一的輔助過濾，非主訊號）。

策略方向：均值回歸（單日 Range Expansion climax + 強日內反轉確認）
    Strategy direction: Mean reversion via single-bar TR expansion climax +
    strong intraday reversal confirmation

迭代歷程（Iteration Log）：

Att1（Baseline）—— 嚴格 climax 定義
    進場：TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10日回檔 [-6%, -20%] + WR(10) ≤ -70
    出場：TP +4.5% / SL -4.0% / 15 天 / cd 10
    結果：Part A n=1 WR 100% TP +4.50% 零方差 Sharpe 0.00；
          Part B n=1 WR 0% SL -4.14% Sharpe 0.00；Part C n=0
    min(A,B) 0.00，訊號觸發率僅 0.4%（500 交易日共 2 訊號）
    失敗分析：TR ≥ 2.0×ATR(20) + ClosePos ≥ 50% 雙硬性過濾極嚴，
        樣本不足以評估策略有效性。

Att2（放寬 TR 倍率與 ClosePos）—— 增加訊號頻率
    進場：TR/ATR(20) ≥ 1.5 + ClosePos ≥ 40% + 其餘同 Att1
    結果：Part A n=1（**不變！**）Sharpe 0.00；
          Part B n=4 WR 25% cum -7.95% Sharpe **-0.53**；Part C n=1 SL
    min(A,B) **-0.53**（顯著惡化）
    失敗分析：(1) Part A 2024 bull regime 下 pullback/WR 為綁定條件，
        TR/ClosePos 放寬無新增觸發；(2) Part B 2025 bear regime 下放寬
        新增 3 訊號全停損——寬 range expansion + 40% ClosePos 在慢磨下跌
        中捕捉「bear rally 假反彈」而非 true capitulation。Regime-dependent
        雙極失敗：Part A 觸發不足、Part B 品質下降。

Att3（嚴格 climax + 放寬 pullback/WR）—— 保留核心主訊號、擴大 regime 候選
    進場：TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10日回檔 [-4%, -20%] + WR(10) ≤ -65
    結果：Part A n=1（**與 Att1 完全相同**）Sharpe 0.00；
          Part B n=1（**與 Att1 完全相同**）Sharpe 0.00；Part C n=0
    min(A,B) 0.00
    失敗分析：放寬 pullback 至 -4% 與 WR 至 -65 對訊號集**完全非綁定**——
        證實 TR/ATR ≥ 2.0 + ClosePos ≥ 50% 本身已隱含深回檔與極端超賣，
        pullback/WR 為後置（redundant）過濾器。IBIT 在 2024-2025 全部 500
        交易日僅 2 日滿足「單日 TR 爆發 + 強日內反轉」——這兩日分散於
        Part A 與 Part B 的不同 regime，產生零方差或對立結果。

總結（結論）：三次迭代均未超越 IBIT-006 Att2 的 min(A,B) 0.40。
    **IBIT 第八次失敗的策略類型**（繼 MR pullback+WR、RSI(2)、BB 擠壓突破、
    波動率自適應、2日急跌過濾、短期動量、Keltner Lower 之後）。

    **Repo 首次單日 Range Expansion 主訊號試驗** 的核心失敗根因：

    1. **訊號稀缺性**：TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% 要求「今日波幅為
       近 20 日均值的 2 倍且收盤過中點」，在 IBIT（3.17% 日波動）上每年
       觸發 ≤ 1-2 次。放寬 TR 至 1.5 擴大 Part B 觸發但全為假反彈停損
       （Att2 證實）；保留 TR 2.0 但放寬其他過濾條件為**非綁定**（Att3 證實）。
       Range Expansion Climax 模式無法在 IBIT 的兩年半數據下產生統計意義
       樣本。

    2. **Range Expansion 本身無「真/假反轉」區分力**：ClosePos ≥ 50% 在單日
       爆發中無法區分「capitulation 買家接回」與「賣壓暫歇後繼續」。Att2
       在 Part B 的 3 筆 SL 訊號（2025 年）皆為 bear rally dead-cat bounce
       後的續跌，與 cross-asset lesson #20b 失敗家族一致——**單日 price-action
       反轉確認在 post-peak/bear regime 結構性無效**。

    3. **與 Gap-Down 結構性差異**：IBIT-006 Att2 Gap-Down 捕捉「盤外連續
       交易 → 美股盤中撿便宜」的特殊結構性不對稱；Range Expansion 僅捕捉
       「盤中劇烈波動 + 日內反轉」，缺乏 gap 的「overnight flushout 完成」
       前置條件。Range Expansion 在傳統（非 24/7 連續標的）市場可能更
       有效，因為隔夜 gap 不構成主要 capitulation 結構。

    **跨資產啟示（待進一步驗證）**：
    - Range Expansion Climax（TR/ATR 單日爆發）作為 MR 主訊號在高波動
      24/7 連續標的（加密 ETF）上訊號過稀疏。
    - 可能適用資產（假設）：傳統美股板塊 ETF（CIBR、XBI）於事件日
      單日爆發後，因無 overnight gap 結構，range expansion 可能為
      capitulation 主要訊號。待驗證。
    - 對於 IBIT，**IBIT-006 Att2 Gap-Down Capitulation + Intraday Reversal
      仍為全域最優**（8 次實驗、24+ 次嘗試）。

資產特性：IBIT 日波動 3.17%，GLD 比率 2.64x。
    最終參數（Att3）：
    進場：TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10 日回檔 [-4%, -20%] + WR(10) ≤ -65
    出場：TP +4.5% / SL -4.0% / 最長持倉 15 天
    冷卻：10 天
    無追蹤停損（日波動 3.17% 禁用區域，cross-asset lesson #2）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBIT008Config(ExperimentConfig):
    """IBIT-008 Range Expansion Climax 均值回歸參數"""

    # Range Expansion 主訊號（Att3：回到嚴格 climax 定義）
    atr_period: int = 20  # ATR 基準期
    tr_ratio_threshold: float = 2.0  # Att3：TR/ATR(20) ≥ 2.0（恢復嚴格 climax）

    # 日內反轉確認（Att3：ClosePos 50% 強日內反轉）
    close_pos_threshold: float = 0.50  # Att3：ClosePos ≥ 50%（恢復嚴格）

    # 回檔深度過濾（Att3：放寬 pullback 至 -4% 以增加 Part A 候選）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.04  # Att3：10 日回檔 ≤ -4%（由 -6% 放寬）
    pullback_upper: float = -0.20  # 回檔上限 -20%（過濾崩盤極端）

    # Williams %R 超賣確認（Att3：放寬 WR 至 -65）
    wr_period: int = 10
    wr_threshold: float = -65.0  # Att3：WR(10) ≤ -65（由 -70 放寬）

    # 冷卻
    cooldown_days: int = 10


def create_default_config() -> IBIT008Config:
    return IBIT008Config(
        name="ibit_008_range_expansion_mr",
        experiment_id="IBIT-008",
        display_name="IBIT Range Expansion Climax Mean Reversion",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.045,  # +4.5%（IBIT-006 Att2 已驗證甜蜜點）
        stop_loss=-0.04,  # -4.0%（IBIT-006 Att2 已驗證甜蜜點）
        holding_days=15,
    )
