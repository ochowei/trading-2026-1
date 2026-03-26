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

<!-- 範例格式：
- **2026-03-25** — 觀察到 VIX 與 TQQQ 跌幅的非線性關係，可進一步量化
-->

---

## 更新紀錄 (Changelog)

| 日期       | 內容                         |
|------------|------------------------------|
| 2026-03-25 | 新增「想嘗試的策略」清單（均值回歸、動能趨勢、量先價行） |
| 2026-03-25 | 建立 HUMAN_PM_MEMO.md，取代 WATCHLIST.md |
| 2026-03-25 | 新增 TQQQ-013（QQQ 過濾 + 優化出場 + 成交模型）失敗紀錄：訊號過少且績效落後 TQQQ-010 |
| 2026-03-25 | 新增「交易執行模型 (Execution Model) 選擇備忘」，標註當前標準與可替換選項 |
| 2026-03-25 | 於「關注標的」清單中新增無相關/負相關資產 ETF (TLT, GLD) 供避險參考 |
| 2026-03-25 | 新增 GLD-001 實驗 (gld_001_mean_reversion)：達到每年約 3 次訊號且近 80% 高勝率的均值回歸策略 |
