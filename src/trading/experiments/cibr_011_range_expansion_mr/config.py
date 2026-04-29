"""
CIBR-011：單日 Range Expansion Climax 均值回歸配置
(CIBR Wide-Range Climax + Intraday Reversal Mean Reversion Config)

動機（Motivation）：
    IBIT-008 三次迭代均失敗（min(A,B) Sharpe 0.00 全部），確認 Range Expansion
    Climax MR 模式在高波動 24/7 連續加密 ETF（IBIT 3.17% vol）上訊號過稀疏。
    跨資產假設（cross_asset_lessons #9 IBIT-008 note）：
        "Range Expansion MR may work on traditional (non-24/7) US sector ETFs
        (CIBR/XBI) where overnight gaps are absent and single-bar TR expansion
        represents primary capitulation structure"

    本實驗為 **CIBR 第 11 個策略**，亦為 **repo 首次將 Range Expansion 主訊號
    試驗於傳統 US 板塊 ETF**（IBIT-008 為加密 ETF；TLT-006 將 range expansion
    僅作多條件之一輔助）。CIBR 1.53% 日波動的網路安全板塊 ETF 為合理候選：
        1. 傳統開盤交易（無 24/7 持續價格發現），TR 完整捕捉日內賣壓
        2. 事件驅動（CrowdStrike 事件、Cisco 財報、政府網路安全預算）
           常產生單日寬範圍下殺/反彈 K 棒
        3. CIBR-009/010 已驗證 Key Reversal Day（多條件 price-action）+ NR7
           （volatility contraction）失敗，但 NR7 為「窄範圍」設計，與
           Range Expansion「寬範圍」結構截然相反

策略方向：均值回歸（單日 Range Expansion climax + 強日內反轉確認）
    Strategy direction: Mean reversion via single-bar TR expansion climax +
    strong intraday reversal confirmation, applied to US sector ETF

成交模型：執行模型回測（隔日開盤市價進場、滑價 0.1%、悲觀認定）
    Execution model: ExecutionModelBacktester (next-open market entry,
    0.1% slippage, pessimistic SL execution)

迭代歷程（Iteration Log）：

Att1（Baseline）—— IBIT-008 結構性參數縮放至 CIBR 1.53% vol
    進場：TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10日回檔 [-3%, -10%]
          + WR(10) ≤ -70
    出場：TP +3.5% / SL -4.0% / 18 天 / cd 8
    結果：Part A 3 訊號 1W/2L WR 33.3% 累計 -4.81% Sharpe **-0.44**
          Part B 2 訊號 2W WR 100% 累計 +7.12% Sharpe 0.00（零方差）
          min(A,B) **-0.44**（遠低於 CIBR-008 Att2 0.39）
    失敗分析：(1) 訊號稀缺（8 年僅 5 訊號，0.6/yr）；
        (2) Part A 兩筆 SL 為 crash precursor 假反轉
        （2020-02-24 COVID 前夕、2021-09-20 Evergrande）；
        (3) Part B 2024 兩筆均勝但樣本過薄無統計意義

Att2（放寬 TR 1.7 + 加 ATR(5)/ATR(20) > 1.10 過濾）
    進場：TR/ATR(20) ≥ 1.7 + ClosePos ≥ 50% + 10日回檔 [-3%, -8%]
          + WR(10) ≤ -70 + ATR ratio > 1.10
    出場：同 Att1
    結果：Part A 2 訊號 1W/1L WR 50% 累計 -0.74% Sharpe **-0.08**
          Part B 2 訊號 1W/1L WR 50% 累計 -1.91% Sharpe **-0.29**
          min(A,B) **-0.29**
    失敗分析：ATR>1.10 過濾器**移除好訊號多於壞訊號**——Part B 2024 兩筆
        winners（2024-02-21、2024-08-05）的 ATR ratio 均 < 1.10 被過濾，
        反捕捉 2025 衰退期 1W 1L。
        **核心發現**：CIBR Range Expansion 高品質訊號偏好「平靜 ATR + 突發
        TR 爆發」結構，與 CIBR-008 BB Lower 框架（需 ATR 升高）方向相反。
        平行 EEM-013（MACD 框架）的 reverse ATR 發現。

Att3（反向 ATR 過濾 ATR(5)/ATR(20) ≤ 1.10）—— 測試平靜 regime 假設
    進場：TR/ATR(20) ≥ 1.7 + ClosePos ≥ 50% + 10日回檔 [-3%, -10%]
          + WR(10) ≤ -70 + ATR ratio ≤ 1.10
    出場：同 Att1
    結果：Part A 2 訊號 0W/2L **WR 0%** 累計 -8.03% Sharpe 0.00
          - 2021-05-04 SL（4天）
          - 2021-09-20 SL（9天）
          Part B **0 訊號**
          min(A,B) **0.00**（Part A WR 0%，Part B 零方差）
    失敗分析：反向 ATR 假設**完全不成立**——
        (1) 移除所有 Part B 訊號（2024-2025 所有候選日 ATR ratio 均 > 1.10），
            包含 Att1 已驗證的 2024-02-21/2024-08-05 雙勝；
        (2) Part A 留下兩筆 SL（2021 兩個事件驅動下殺後續跌），
            ATR ≤ 1.10 反而保留「正在累積下跌動能但 ATR 尚未飆升」的危險
            訊號，這正是 false capitulation。
        (3) ATR 過濾在 CIBR Range Expansion 上**無單向有效性**——
            正向（>1.10）移除好訊號、反向（≤1.10）保留壞訊號。

總結（結論）：三次迭代均未超越 CIBR-008 Att2 的 min(A,B) 0.39。

    **CIBR 第 7 個失敗的策略類型**（繼 BB Squeeze、RSI(2)、20日回看、
    RS 動量、Key Reversal Day、NR7 之後）。

    **Repo 首次將 Range Expansion Climax MR 試驗於傳統 US 板塊 ETF** 的
    核心失敗根因：

    1. **訊號稀缺性結構性問題**：TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% 在 CIBR
       8 年資料僅 5 訊號（0.6/yr），與 IBIT-008 同樣稀疏。放寬 TR 至 1.7
       可增加候選但 quality discrimination 不足。

    2. **Range Expansion 本身無「真/假反轉」區分力**（cross-asset 一致發現）：
       與 IBIT-008 平行，ClosePos ≥ 50% 在單日爆發中無法區分「capitulation
       買家接回」與「賣壓暫歇後繼續」。Att1 Part A 兩筆 SL（2020-02-24
       COVID、2021-09-20 Evergrande）皆為事件驅動下殺後續跌，與
       cross-asset lesson #20b 失敗家族（V-bounce ≠ genuine reversal）一致。

    3. **ATR 過濾器無單向有效性**：
       - 正向 ATR (>1.10)：移除 Part B 2024 兩筆 winners（低 ATR 環境的
         真 capitulation），net 損害 Sharpe
       - 反向 ATR (≤1.10)：移除所有 Part B 訊號，留下 Part A 兩筆 SL（事件
         驅動下殺早期，ATR 尚未飆升）
       揭示 CIBR Range Expansion 訊號的「ATR 環境」與「真假反轉」**無單向
       關聯**——ATR 為 noise，無法作為品質過濾。

    4. **與 CIBR-008 BB Lower 框架的結構性差異**：CIBR-008 BB(20,2.0) 下軌
       觸及為**統計自適應**進場（隨 BB 標準差自動縮放），且配合 ATR>1.15
       過濾為**正向 ATR 框架**。Range Expansion 為**單日點估計**進場，
       缺乏統計自適應特性，且 ATR 雙向皆無效。

    **跨資產啟示**：
    - **拒絕 IBIT-008 跨資產假設**：「Range Expansion MR 可能適用傳統 US
      板塊 ETF」於 CIBR 上不成立。Range Expansion 失敗家族擴展至：
      (a) 高波動 24/7 加密 ETF（IBIT 3.17% vol）
      (b) 中波動傳統 US 板塊 ETF（CIBR 1.53% vol）
    - **整合 lesson #20b**：所有 entry-time 過濾器（oscillator hook、
      day-after reversal、capitulation depth、single-bar range expansion）
      在「事件驅動 + 缺乏統計自適應」的進場框架下結構性失效。
    - **可能仍適用資產（待驗證）**：高頻內生波動的個股（TSLA/NVDA）
      財報日 range expansion 後的均值回歸——但 CIBR/XBI 類事件驅動板塊
      ETF 已證明不適用。
    - **CIBR 全域最優仍為 CIBR-008 Att2**（10 次實驗、30+ 次嘗試），
      BB Lower + Pullback Cap 混合進場為 1.5-2.0% vol 板塊 ETF 的最優結構。

最終參數（Att3）：
    進場：TR/ATR(20) ≥ 1.7 + ClosePos ≥ 50% + 10 日回檔 [-3%, -10%]
          + WR(10) ≤ -70 + ATR(5)/ATR(20) ≤ 1.10
    出場：TP +3.5% / SL -4.0% / 最長持倉 18 天
    冷卻：8 天
    無追蹤停損（CIBR 1.53% vol 為 trailing stop 邊緣區，且 MR 框架直接
    用固定 TP/SL 已驗證最優）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR011Config(ExperimentConfig):
    """CIBR-011 Range Expansion Climax 均值回歸參數（Att3：反向 ATR）"""

    # Range Expansion 主訊號（Att3：保留 1.7 寬鬆門檻）
    atr_period: int = 20  # ATR 基準期
    tr_ratio_threshold: float = 1.7

    # 日內反轉確認（Att3：保留 ClosePos ≥ 50%）
    close_pos_threshold: float = 0.50

    # 回檔深度過濾（Att3：恢復 -10% cap 以保留 2024 訊號集）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_upper: float = -0.10  # Att3：恢復 -10%（Att2 的 -8% 過嚴）

    # Williams %R 超賣確認
    wr_period: int = 10
    wr_threshold: float = -70.0

    # 反向 ATR 過濾（Att3 新發現）：ATR(5)/ATR(20) ≤ 1.10
    # 假設：平靜波動率 + 單日 TR 爆發 = 真正 capitulation（vs. 持續高波動的 SL 續跌）
    # 平行 EEM-013（MACD 框架）的反向 ATR 發現（cross-asset lesson #6）
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_max: float = 1.10  # Att3：上限（calm regime 過濾）

    # 冷卻
    cooldown_days: int = 8


def create_default_config() -> CIBR011Config:
    return CIBR011Config(
        name="cibr_011_range_expansion_mr",
        experiment_id="CIBR-011",
        display_name="CIBR Range Expansion Climax Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%（CIBR-008 已驗證）
        stop_loss=-0.04,  # -4.0%（CIBR-008 已驗證）
        holding_days=18,
    )
