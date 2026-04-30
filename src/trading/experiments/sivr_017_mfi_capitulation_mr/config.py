"""
SIVR-017：Money Flow Index (MFI) Capitulation Mean Reversion 配置
(SIVR Volume-Weighted Capitulation Mean Reversion)

動機（Motivation）：
    SIVR-015 Att1（RSI(14) bullish hook + pullback+WR）以 min(A,B) 0.48 為
    全域最優，但 Part A 仍殘留 2 筆 stop-loss（2021-09-21, 2023-02-07），
    兩日皆出現「RSI 已 hook turn-up，但成交量並未確認 capitulation」。
    SIVR 為白銀礦業 ETF（避險 + 工業雙屬性），高量恐慌折價的賣壓資訊量
    遠高於低量緩跌——純粹 price-based RSI(14) 無法捕捉這個區隔。

    Money Flow Index (MFI) 為 volume-weighted RSI：以 typical price (H+L+C)/3
    × volume 累計正負資金流，產生 0-100 oscillator。MFI ≤ 20 為傳統
    overbought/oversold 門檻，相較 RSI 多了「成交量加權」這一維度。

    本實驗為 **repo 首次 MFI 試驗**（2026-04-30 為止 repo 內未有任何
    Money Flow / Chaikin / Volume-weighted 振盪器主訊號實驗）。

策略方向：均值回歸（volume-confirmed capitulation detection）
    Strategy direction: Mean reversion via volume-weighted oversold filter

挑戰目標：min(A,B) > 0.48（SIVR-015 Att1 全域最優）

新方向價值（cross-asset）：
    1. 若 MFI 在 SIVR 上有效，則確認 volume-weighted 振盪器作為主品質過濾器
       對「avtive MR regime + 高量驅動」資產（白銀礦業 / 工業金屬 / 加密）
       有泛用性，可跨資產移植 COPX/SIVR/IBIT 等
    2. 若 MFI 失敗，則確認 SIVR 的 capitulation 結構並非「成交量區隔」型，
       而是 price-momentum 型——與 lesson #20b RSI hook 結論一致

========================================================================
三次迭代記錄（2026-04-30，成交模型 0.15% slippage，隔日開盤市價進場）：
========================================================================

Att1：MFI(14) ≤ 25 oversold + SIVR-005 base（pullback 7-15% + WR(10) ≤ -80）
       TP +3.5%/SL -3.5%/15d/cd 10
  Part A: 8 訊號 WR 37.5% Sharpe **-0.28** cum -7.89% MDD -6.86%
          3 TPs + 5 SLs（2020-09-22/2021-12-03/2022-05-02/2022-07-07/2023-02-15）
  Part B: 2 訊號 WR 100% Sharpe 0.00（zero-var）cum +7.12%
  min(A,B) **-0.28**（-158% vs SIVR-015 Att1 的 0.48）
  失敗分析：MFI ≤ 25 為「volume-weighted 深度超賣」，捕捉的是「下跌中段
  量增急跌」訊號（價格仍在下挫），而非 capitulation 尾聲。Part A 5 SLs
  集中於 2020-09 銀價 hike-fear、2021-12 Fed 鷹派、2022 升息熊市、
  2023-02 SVB pre-shock 等持續下跌期。確認 MFI 標準 oversold 閾值在
  SIVR 上選擇早期 panic（仍續跌）而非後期 capitulation（已反轉）。

Att2：MFI bullish hook（lookback 5d / delta ≥ 3 / near-low MFI ≤ 35）
       無 RSI hook，其他同 SIVR-005 base
  Part A: 9 訊號 WR 55.6% Sharpe **0.09** cum +2.40% MDD -6.06%
  Part B: 3 訊號 WR 66.7% Sharpe **1.41** cum +7.12% MDD -3.39%
          （2024-07-26 TP / 2024-11-12 expiry 0% / 2025-04-07 TP）
  min(A,B) **0.09**（-81% vs SIVR-015 Att1 的 0.48）
  失敗分析：MFI hook 採用 RSI hook 同樣的 turn-up 邏輯（自 5d 低點回升
  ≥3 點，且 5d 低點曾 ≤ 35），結構性參數對齊 SIVR-015。Part A 9 訊號中
  4 SLs（2021-09-21、2021-11-30、2022-05-05、2022-08-23）多為「MFI
  hook 觸發但價格仍續跌」結構。Part A 3 SLs 為 SIVR-015 同期 SLs（2021-09-21
  shared）+ 1 個 SIVR-015 沒有的新 SL（2022-08-23）；新增 4 TPs 中
  2019-09-30、2023-03-07 為 RSI hook 沒抓到的訊號。MFI hook 與 RSI hook
  訊號集合**部分正交**（重疊 ~38%），但 MFI hook 加入的訊號品質低於 RSI
  hook 加入的訊號。Part B 3 訊號中 2024-11-12 與 SIVR-015 Att1 重疊，
  其餘為 MFI hook 獨有訊號（不重疊 SIVR-015 Att1 Part B 的 2024-05-02、
  2024-08-07）——驗證 MFI hook 在 SIVR Part B 上仍有合理 selectivity，
  但 Part A 整體選擇力低於 RSI hook。

Att3（ablation + 疊加）：MFI hook（同 Att2）+ RSI(14) bullish hook（SIVR-015
       Att1 同參數）雙重 capitulation 確認
  Part A: 5 訊號 WR **80.0%** Sharpe **0.73** cum +10.58% MDD -6.06%
          4 TPs（2020-11-30、2022-05-11、2022-07-13、2023-08-10）
          + 1 SL（2021-09-21，無法被任何過濾器移除的「真 capitulation 結構」）
  Part B: 1 訊號（2024-11-12 expiry 0%）zero-var Sharpe 0.00
  min(A,B) **0.00**（Part B over-filter）
  Part A 獨立 Sharpe 0.73 為 SIVR 系列 in-sample 最高 +52% vs SIVR-015 Att1）
  失敗分析：(1) Part A 達到 80% WR、Sharpe 0.73 ≫ baseline，stack 雙重
  hook 嚴格過濾器移除了 2021-06-21 expiry +1.42%（small win）+
  2023-02-07 SL（成功移除）+ 2023-06-23 TP（誤殺）三筆，淨效果為 WR 升高
  + 平均報酬升高 + Sharpe 升高；(2) 但 Part B 只剩 1 筆 2024-11-12 zero-return
  expiry，移除 SIVR-015 Att1 的 2024-05-02 TP 與 2024-08-07 TP 兩筆贏家——
  雙 hook 在 Part B 變得**結構性互斥**：MFI hook 與 RSI hook 在 SIVR Part B
  的觸發日**幾乎不重疊**（MFI hook 抓 2024-07-26、2025-04-07；RSI hook 抓
  2024-05-02、2024-08-07；兩者唯一交集為 2024-11-12 zero-return expiry）。
  Stack 結果為兩 hook 交集的「下界」訊號，在低 signal-count 資產上必然
  over-filter。

========================================================================
整體失敗結論（3 次嘗試均未超越 SIVR-015 Att1 min(A,B) 0.48）：
========================================================================
1. **MFI 標準 oversold 閾值（≤ 25）在 SIVR 上完全錯誤方向**：MFI ≤ 25
   選擇 high-volume 急跌期（價格仍續跌）而非 capitulation 尾聲（已反轉），
   Part A 5 SLs 確認 MFI 深度 oversold 並無 reversal selectivity。

2. **MFI hook（自低點回升）為合理結構但選擇力次於 RSI hook**：MFI hook
   與 RSI hook 結構平行（turn-up + max-min oversold），但在 SIVR 2.34% vol
   上 MFI hook 加入的 Part A 訊號品質普遍低於 RSI hook。MFI hook 與 RSI
   hook **部分正交**（訊號集合重疊 ~38%），確認 volume-weighted 與
   price-only 振盪器抓不同日期。

3. **MFI hook + RSI hook stack over-filter Part B**：兩 hook 在 SIVR Part B
   觸發日幾乎不重疊，stack 交集只剩 1 筆 zero-return expiry。雖 Part A
   Sharpe 0.73 ≫ baseline 0.48，但 Part B over-filter 使 min(A,B) = 0.00。
   此為 stack 雙振盪器在低 signal-count 資產上的**結構性失敗模式**。

4. **Repo 首次 MFI 試驗失敗**——擴展 lesson #6 至 volume-weighted 振盪器
   類別：MFI 作為主要 capitulation 過濾器在已飽和 RSI hook 框架（SIVR-015
   Att1）上**無邊際品質提升**，平行 URA-011 Volume spike 結論
   （Volume filter 創造 A/B 對稱性但不突破品質天花板）。**MFI 與 Volume
   spike 共同結論**：volume-based filters 在 price-momentum-driven MR
   策略上為 supplementary 而非 substitutive 維度。

5. **擴展 lesson #20b 失敗家族至 volume-weighted oscillator hook 類別**：
   MFI hook（容量加權版 RSI hook）在 SIVR 上**結構性次於 RSI hook**——
   不是同一失敗家族（V-bounce ≠ genuine reversal），而是相反——MFI hook
   在 active MR regime 上 functional but suboptimal，因 SIVR 的 capitulation
   結構由 price momentum 主導而非 volume profile。新跨資產規則：volume-
   weighted oscillators 適用於 volume-driven assets（如 individual stocks
   with earnings spikes），對 ETF（成份分散）幫助有限。

跨資產規則（新）：
  - MFI ≤ 20-25 標準 oversold 閾值不適用於 SIVR/silver ETF 類資產
    （捕捉早期 panic 而非 capitulation 尾聲）
  - MFI hook（turn-up + max-min oversold）為合理結構但 selectivity 次於
    RSI hook 在 active MR regime ETF 上
  - 雙振盪器 hook stack（MFI + RSI）為結構性互斥，over-filter 低 signal-
    count Part B
  - Volume-weighted 振盪器（MFI、CMF、Force Index）作為主訊號需先驗證
    資產的 capitulation 結構是否為 volume-driven（個股 earnings vs ETF
    分散持有）

SIVR 特有限制（已確認）：
  - SIVR-015 Att1（RSI(14) hook + pullback+WR）持續為全域最優（min 0.48）
  - SIVR-017 Att3 stack 雖 Part A Sharpe 0.73 達歷史新高，但 Part B over-
    filter 使整體 min 0.00，無法作為實戰策略
  - 確認 SIVR 的 MR 核心為「price momentum reversal」（RSI hook）而非
    「volume capitulation」（MFI hook）——與 SIVR-016 WVF 失敗結論一致
    （capitulation depth 並非 SIVR MR 信號的核心驅動力）

資產特性：SIVR 日波動 2.34%，GLD 比率 1.5-2x。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVR017Config(ExperimentConfig):
    """SIVR-017 MFI Capitulation MR 參數"""

    # 進場指標（同 SIVR-005 / SIVR-015 base）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥ 7%
    pullback_cap: float = -0.15  # 回檔 ≤ 15%
    wr_period: int = 10
    wr_threshold: float = -80.0

    # MFI 主過濾器
    mfi_period: int = 14
    # MFI bullish hook 模式（Att2/Att3 採用）
    mfi_hook_enabled: bool = True
    mfi_hook_lookback: int = 5  # 觀察過去 N 日內 MFI 最低點
    mfi_hook_delta: float = 3.0  # MFI 需自近期低點回升 ≥ H 點
    mfi_hook_max_min: float = 35.0  # 近期 MFI 低點須曾 ≤ 此水位（volume-weighted oversold）
    # 簡單 MFI 閾值（Att1 採用 oversold ≤ N，已驗證失敗）
    mfi_threshold: float = 100.0  # 預設不綁定（Att2/Att3 改採 hook 模式）

    # 是否疊加 RSI(14) bullish hook（Att3 試驗 MFI hook + RSI hook 雙重 capitulation 確認）
    rsi_hook_enabled: bool = False
    rsi_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0

    cooldown_days: int = 10


def create_default_config() -> SIVR017Config:
    return SIVR017Config(
        name="sivr_017_mfi_capitulation_mr",
        experiment_id="SIVR-017",
        display_name="SIVR MFI Capitulation MR",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,
    )
