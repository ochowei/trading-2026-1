# 研究備忘錄 (Research Memo)

> 本文件記錄未來的研究與開發方向，取代原本的 `WATCHLIST.md`。

## 關注標的 (Watchlist)

| 標的 | 類型 | 說明 |
|------|------|------|
| SPY | ETF | S&P 500 指數 ETF，美股大盤代表 |
| QQQ | ETF | Nasdaq-100 指數 ETF，科技股為主 |
| DIA | ETF | 道瓊工業指數 ETF，藍籌股為主 |
| IWM | ETF | Russell 2000 小型股指數 ETF |
| TQQQ | 槓桿 ETF | Nasdaq-100 三倍做多槓桿 ETF |
| SOXX | ETF | 費城半導體指數 ETF |
| SOXL | 槓桿 ETF | 半導體三倍做多槓桿 ETF |
| AAPL | 個股 | Apple，全球市值最大企業之一 |
| MSFT | 個股 | Microsoft，雲端與 AI 雙引擎 |
| GOOGL | 個股 | Alphabet (Google)，搜尋與廣告龍頭 |
| AMZN | 個股 | Amazon，電商與雲端 (AWS) 巨頭 |
| META | 個股 | Meta Platforms，社群媒體與 AI 投資 |
| NVDA | 個股 | NVIDIA，AI 晶片與 GPU 龍頭 |
| AMD | 個股 | AMD，CPU 與 GPU 競爭者 |
| TSLA | 個股 | Tesla，電動車與能源領導品牌 |
| TLT | ETF | 美國 20 年期以上公債 ETF，避險與利率指標 |
| GLD | ETF | SPDR 黃金 ETF，抗通膨與避險資產 |

---

## 想嘗試的策略

1. 均值回歸
2. 動能趨勢
3. 量先價行

---

## 開發任務 (Development Tasks)

### 進行中 (In Progress)

1. **設計新實驗以取得更好結果**
   - 閱讀各標的既有實驗的 AI Agent 快速索引
   - 針對各標的，根據已有實驗的教訓與未嘗試方向，設計並執行新實驗
   - 將實驗中學到的知識更新至各 EXPERIMENTS_*.md（包含其 AI Agent 快速索引），以及 `.agents/context/cross_asset_lessons.md`

2. **彙整各標的最佳實驗結果至 Trading Followup**
   - 取得每個標的目前表現最好的實驗
   - 評估是否達到「足夠好」的標準（勝率、報酬風險比、訊號頻率）
   - 將符合標準的實驗納入 `uv run trading followup` 的輸出範疇

3. **每日開盤前執行 Trading Followup Summary**
   - 每天美股開盤前（台灣時間晚上 9:30 前）執行 `uv run trading followup`
   - 查看當天可進行的進場/出場操作
   - 依據訊號決定是否下單

---

## 交易執行模型 (Execution Model) 選擇備忘

紀錄當前標準設定與未來可替換的選項，供新策略參考（若需套用新選項，需先擴充 `ExecutionModelBacktester` 引擎）：

**1. 當前標準配置 (TQQQ-010 之後的防禦型流程)**
- **進場 (Entry)**: `next_open_market` (隔日開市市價)
- **停損 (Stop Loss)**: `stop_market` GTC (取消前有效停損市價)
- **止盈 (Profit Target)**: `limit_order` Day (當日有效限價止盈)
- **到期出場 (Expiry)**: `next_open_market` (隔日開市市價)
- **日內路徑假設 (Intrabar)**: **悲觀認定 (Pessimistic)**（單日 K 線同時觸發停損與止盈時，假定最差狀況「停損先成交」，防過度擬合）

**2. 可替換選項 (Firstrade 券商支援 / 未來實驗可考慮)**
- **進場可替換**:
  - `next_open_limit` (隔日開盤限價): 避開跳空開高追高的滑價損失；但需承擔「未成交而錯失機會 (Unfilled)」的風險。
- **出場可替換**:
  - `stop_limit` (停損限價): 防範閃崩 (Flash Crash) 導致的極端滑價；但跌速過快時可能錯過停損點，導致被深套。
  - `trailing_stop` (移動停損): 隨股價創高自動推升停損點，能取代固定目標價讓獲利放膽奔跑；但容易被盤中毛刺跌破而無辜洗下車。
- **日內假設可替換**:
  - `Optimistic` (樂觀認定) 或 `Random` (機率分派)：回測績效容易虛高，通常維持現行的「悲觀認定」能確保績效最穩健。

---

## 回測區間與過擬合防護策略

### 現行回測區間

| 區間 | 期間 | 用途 |
|------|------|------|
| Part A (In-Sample) | 2019-01-01 ~ 2023-12-31 | 策略開發與參數調整 |
| Part B (Out-of-Sample) | 2024-01-01 ~ 2025-12-31 | 驗證泛化能力，納入 followup 的主要依據 |
| Part C (Live) | 2026-01-01 ~ 至今 | 實盤追蹤 |

### 決策：Part A/B 不隨時間推移

Part A/B 固定不動，理由：
- 它們是策略設計時的歷史紀錄，移動會破壞原始 out-of-sample 的完整性
- 重跑舊實驗後數字不同，文件追溯會混亂
- Part C 自然成為新的驗證層，且是唯一「策略上線後才產生」的數據

**持續驗證靠兩個機制：**
1. `uv run trading analyze` 的滾動窗口會自動涵蓋最新數據
2. Part C 累積足夠樣本後（≥ 3 筆交易），應加入 evaluate-best 的判定條件

### 現行防過擬合機制

| 層級 | 機制 | 防護什麼 |
|------|------|----------|
| 1 | Part A/B 分離 | 參數不在驗證集上調整 |
| 2 | A/B 一致性（WR 差 < 15pp） | 過度擬合 Part A 的策略會在 B 崩潰 |
| 3 | 滾動窗口漸變性評估 | 策略是否對特定 regime 敏感 |
| 4 | 悲觀成交模型 | TP/SL 同日觸及時假設最差情況 |

### 已知漏洞：多重測試問題 (Multiple Testing)

為同一資產設計多個實驗後，即使沒有直接在 Part B 調參數，設計者已經知道 Part B 的市場環境（2024-2025 的行情），會不自覺影響策略設計。跑 N 個實驗後，有 1 個在 Part B 表現好可能只是運氣——這是 p-hacking 的變形。

### 建議補強方向

**短期（低成本）：**
- **重視 Part C 表現**：Part C 是唯一不可能被 peek 的數據。當 Part C 勝率明顯低於 Part B（差距 > 20pp），應發出警告或從 followup 移除
- **記錄策略設計時間**：在 EXPERIMENTS 文件標記設計日期。2026 年設計的策略，Part B 已不是真正的 out-of-sample

**中期（需開發）：**
- **Walk-forward validation**：每個窗口用前半段選參數、後半段驗證，多窗口都穩定才算通過
- **策略數量懲罰**：同一資產實驗越多，Part B 通過門檻應越高（類似 Bonferroni correction）

---

<!-- 範例格式：
- **2026-03-25** — 觀察到 VIX 與 TQQQ 跌幅的非線性關係，可進一步量化
-->

---

## 更新紀錄 (Changelog)

| 日期       | 內容                         |
|------------|------------------------------|
| 2026-04-02 | 新增「回測區間與過擬合防護策略」：Part A/B 固定不移、Part C 持續驗證、多重測試漏洞與補強方向 |
| 2026-04-02 | 新增 USE_CASES.md — 所有可用操作情境與指令的快速參考 |
| 2026-03-29 | 新增「開發任務」區塊，記錄三項進行中任務：設計新實驗、彙整最佳結果至 Followup、每日開盤前執行 Followup |
| 2026-03-29 | 將本文件移入 pm/ 資料夾 |
| 2026-03-25 | 新增「想嘗試的策略」清單（均值回歸、動能趨勢、量先價行） |
| 2026-03-25 | 建立 HUMAN_PM_MEMO.md，取代 WATCHLIST.md |
| 2026-03-25 | 新增 TQQQ-013（QQQ 過濾 + 優化出場 + 成交模型）失敗紀錄：訊號過少且績效落後 TQQQ-010 |
| 2026-03-25 | 新增「交易執行模型 (Execution Model) 選擇備忘」，標註當前標準與可替換選項 |
| 2026-03-25 | 於「關注標的」清單中新增無相關/負相關資產 ETF (TLT, GLD) 供避險參考 |
| 2026-03-25 | 新增 GLD-001 實驗 (gld_001_mean_reversion)：達到每年約 3 次訊號且近 80% 高勝率的均值回歸策略 |
