# Use Cases 總覽

> 本文件描述系統的主要使用情境與對應的 skill / 指令。
> AI Agent 可參考此文件快速判斷該用哪個 skill。
>
> - **validated**: 2026-04-02
> - **data_through**: 2026-04-02

---

## 1. 新增實驗（既有資產）— `/new-experiment`

為已有實驗的資產新增一個變體（例如 GLD-007 → GLD-008）。

**適用時機：** 資產已有至少一個實驗，想嘗試不同參數或策略方向。

**流程：**

1. 讀 `cross_asset_lessons.md` + `EXPERIMENTS_<TICKER>.md` AI_CONTEXT，確認禁忌與已失敗方向
2. 從 `_template/` 複製 4 個檔案（`__init__.py`, `config.py`, `signal_detector.py`, `strategy.py`），必須繼承 `ExecutionModelStrategy`
3. 更新 `EXPERIMENTS_<TICKER>.md`（實驗列表、參數對照表、AI_CONTEXT）
4. 更新 `.github/workflows/tqqq-backtest.yml` 加入新選項
5. Lint / format 驗證 → `uv run trading list` 確認註冊 → `uv run trading run` 執行回測

**涉及檔案：**

- `src/trading/experiments/<ticker>_NNN_<name>/`（新建 4 檔）
- `src/trading/experiments/EXPERIMENTS_<TICKER>.md`
- `.github/workflows/tqqq-backtest.yml`

---

## 2. 新增資產（全新標的）— `/launch-new-asset`

為從未有實驗的新 ticker 建立第一個實驗（例如 SLV-001）。

**適用時機：** 想開始追蹤一個全新的交易標的。

**流程：**

1. 確認 ticker 不存在、讀 cross_asset_lessons 的波動率分類與禁忌
2. 下載 5 年歷史數據，計算日波動率，依波動率選模板：
   - 低波動（< 2%）→ GLD-007 模式（pullback + trailing stop）
   - 中波動（2–4%）→ SIVR-003 模式（pullback，無 trailing stop）
   - 高波動（> 4% 或槓桿型）→ TQQQ-010 模式（極端恐慌買入）
   - 個股高 beta → FCX-001 模式（triple filter，寬出場）
3. 按 vol_ratio 縮放參數（1.5–2.3x）
4. 建立 4 個程式檔 + 新建 `EXPERIMENTS_<TICKER>.md`
5. 更新 `CLAUDE.md`（按需參考連結）、GitHub workflow
6. 執行回測驗證健康指標（A/B signal ratio 0.5–2.0:1，win rate > 50%）

**涉及檔案：**

- `src/trading/experiments/<ticker>_001_<name>/`（新建 4 檔）
- `src/trading/experiments/EXPERIMENTS_<TICKER>.md`（新建）
- `CLAUDE.md`（更新按需參考 + 規則段落）
- `.github/workflows/tqqq-backtest.yml`

---

## 3. 執行實驗與更新結果 — `/run-experiment` + `/update-experiment-docs`

執行回測並將結果記錄到文件。

**適用時機：** 新建實驗後首次執行、或重新執行以取得最新數據的結果。

**流程：**

1. `uv run trading run <name>` — 分 Part A（2019–2023 樣本內）、Part B（2024–2025 樣本外）、Part C（2026+ 實盤）回測，結果存 `results/<name>/latest.json`
2. `uv run trading analyze <name>` — 2 年滾動窗口穩定性分析，判定「漸變 / 突變」
3. `/update-experiment-docs` — 將 JSON 結果回填到 `EXPERIMENTS_<TICKER>.md` 的結果表格與 AI_CONTEXT

**涉及檔案：**

- `results/<name>/latest.json`（產出）
- `src/trading/experiments/EXPERIMENTS_<TICKER>.md`（更新結果表格）

---

## 4. 跟單訊號產生 — `uv run trading followup`

每日產生實際交易指令，供 Firstrade 下單。

**適用時機：** 每個交易日開盤前執行，取得當日下單指令。

**核心邏輯：**

- `followup.py` 中的 `STRATEGIES` 列表記錄每個資產的最佳實驗
- 對每個策略：抓最近 365 天數據 → 計算指標 → 取最近 60 天偵測訊號 → 回測
- 輸出：合併下單表（BUY MARKET / SELL LIMIT / SELL STOP）、持倉狀態、trailing stop 更新提醒

**產出的下單類型：**

| 類型 | 效期 | 說明 |
|------|------|------|
| BUY MARKET | Day | 開盤市價買入 |
| SELL LIMIT | Day | 目標價賣出，收盤自動取消，隔日需重掛 |
| SELL STOP | GTC | 停損單，持續有效直到成交或手動取消 |
| Trailing Stop | 手動每日調整 | 依當日最高價更新停損價 |

**涉及檔案：**

- `src/trading/followup.py`（`STRATEGIES` 列表 + 產出邏輯）

---

## 5. 評估最佳實驗 — `/evaluate-best`

判斷某資產哪個實驗最好，決定是否納入 followup。

**適用時機：** 資產有多個實驗完成回測後，選出最佳者。

**門檻（全部須通過）：**

- Part B win rate ≥ 55%
- Part B 累積報酬 > 0%
- Part B 年訊號數 ≥ 2
- A/B win rate 差距 < 15 個百分點
- 使用 `ExecutionModelStrategy`
- 滾動窗口分析至少一項為「漸變」

**排名優先序（符合門檻後）：**

1. Part B cumulative return（越高越好）
2. Part B Sharpe ratio（平手時的 tiebreaker）

**涉及檔案：**

- `results/<name>/latest.json`（讀取各實驗結果）
- `src/trading/followup.py`（更新 `STRATEGIES`）

---

## 6. 重建 followup 清單 — `/rebuild-followup`

從零重新評估所有資產，重建 `STRATEGIES` 列表。

**適用時機：** 大量實驗結果更新後、或懷疑現有清單不是最優時。

**流程：**

1. 清空 `STRATEGIES` 列表
2. 從 `uv run trading list` 提取所有 ticker
3. 對每個 ticker 執行 `/evaluate-best` 流程
4. 匯整結果、更新 `STRATEGIES`
5. 驗證：lint + `uv run trading followup` 可正常執行

**涉及檔案：**

- `src/trading/followup.py`（重寫 `STRATEGIES`）

---

## 7. 知識新鮮度管理 — `uv run trading freshness`

掃描所有文件的 `data_through` 日期，標記過期知識。

**適用時機：** 定期檢查、或設計新實驗前確認參考資料是否仍然有效。

**判定標準：** `data_through` 距今超過 6 個月 → 標註「基於較舊數據，建議先重新驗證」

**涉及檔案：**

- `src/trading/experiments/EXPERIMENTS_*.md`（掃描 AI_CONTEXT 的日期）
- `.agents/context/cross_asset_lessons.md`（掃描教訓的日期）

---

## 8. 實驗前研究 — `/pre-experiment-research`

設計新實驗前，收集該資產的背景資訊。

**適用時機：** 開始設計新實驗之前，需要了解資產特性與已知教訓。

**產出：**

- 資產波動率特性與分類
- 已掃描的參數空間
- 已證明無效的方向
- 跨資產教訓中的相關規則
- 建議的下一步實驗方向

---

## 9. 實驗驗證 — `/validate-experiment`

驗證實驗程式碼品質與執行結果的合理性。

**適用時機：** 實驗建立完成後、提交 PR 前的最終檢查。

**檢查項目：**

- `uv run ruff check src/` — lint 通過
- `uv run ruff format --check src/` — 格式通過
- `uv run trading list` — 實驗可被發現
- `uv run trading run <name>` — 可正常執行
- 結果合理性（訊號數、win rate、A/B 一致性）

---

## Quick Reference：情境 → Skill 對照

| 我想要... | 使用 |
|-----------|------|
| 為既有資產加一個新實驗 | `/new-experiment <TICKER> <描述>` |
| 開始追蹤全新標的 | `/launch-new-asset <TICKER> <描述>` |
| 跑回測看結果 | `/run-experiment <experiment_name>` |
| 把回測結果寫進文件 | `/update-experiment-docs <experiment_name>` |
| 選出某資產的最佳實驗 | `/evaluate-best <TICKER>` |
| 重建整個 followup 清單 | `/rebuild-followup` |
| 檢查知識是否過期 | `uv run trading freshness` |
| 設計實驗前先做功課 | `/pre-experiment-research <TICKER>` |
| 提交前驗證實驗 | `/validate-experiment <experiment_name>` |
| 產生今日下單指令 | `uv run trading followup` |
