# AI Agent 工作規範

## 1. 程式碼與文件一致性

AI Agent 在修改專案時，必須確保程式碼與文件保持同步：

- **新增或修改功能時**：同步更新相關文件（如 `README.md`、API 文件、註解等），使其準確反映最新的程式碼行為。
- **刪除功能時**：移除文件中對應的描述，避免留下過時或誤導性的內容。
- **修改設定或參數時**：更新文件中的設定說明、範例與預設值。
- **變更檔案結構時**：更新文件中的目錄結構說明與檔案路徑參照。

> 任何程式碼的變更都不應導致文件與實際行為不一致。若發現既有的不一致，應主動修正。

## 2. 回測與實盤貼近原則（成交模型）

為了讓後續研究更貼近實盤，新增以下規範：

- **舊實驗既往不咎（Grandfathered）**：
  - 既有實驗（已存在於 `src/trading/experiments/` 的策略）不強制回補成交模型，可維持原始回測邏輯與既有結果，以保留歷史可比性。
  - 既往不咎的實驗編號（目前已完成）：
    - `TQQQ-001`
    - `TQQQ-002`
    - `TQQQ-003`
    - `TQQQ-004`
    - `TQQQ-005`
    - `TQQQ-006`
    - `TQQQ-007`
    - `TQQQ-008`
    - `TQQQ-009`
  - 若未來 `src/trading/experiments/EXPERIMENTS_TQQQ.md` 新增編號，預設不自動納入既往不咎，需在本規範明確追加後才生效。
- **新實驗強制納入成交模型（Required for future experiments）**：
  - 自本規範更新後，所有新建實驗必須在回測中明確定義並實作成交模型，不可再默認「訊號必成交」。
  - 至少需包含：
    1. **進場模式**（例如 `next_open_market` 隔日開市市價 / `next_open_limit` 隔日開市限價）
    2. **出場模式**（基於 Firstrade 支援之功能，例如 `limit_order` (限價止盈) / `stop_market` (停損市價) / `stop_limit` (停損限價) / `trailing_stop` (移動停損) / `next_open_market` (隔日訊號出場市價)）
    3. **未成交處理**（非常重要，需模擬限價單/停損單未觸價之情況，例如委託單為 Day (當日有效) 則收盤取消，或 GTC (取消前有效) 則遞延至隔日，或視為錯失機會）
    4. **成交統計**（至少揭露 filled / unfilled 數量與成交率）
    5. **日內路徑假設 (Intrabar Assumption)**：若實驗同時使用「限價/觸價進場」與「盤中觸價出場 (如停損/停利)」，必須在程式碼與實驗文件中明確定義單根日 K 線內的觸發先後順序（建議採取 **「悲觀認定 Pessimistic Execution」** 原則：若最高與最低價皆穿越限價與停損價，強制假定發生最差的虧損結果，避免高估績效）。
- **文件同步要求**：
  - 新實驗若引入成交模型，必須同步更新 `README.md` 的實驗說明與參數/假設描述，確保讀者可辨識其與舊實驗的差異。

## 3. 專案檔案用途說明

### 文件類（Markdown）

| 檔案 | 用途 |
|------|------|
| `README.md` | 專案總覽、快速開始指南、新實驗建立教學 |
| `STRUCTURE.md` | 專案資料夾結構與架構說明 |
| `CLAUDE.md` | Claude Code 的專案規則入口，指引 AI 遵循本規範 |
| `.agents/rules/ai-agent-guidelines.md` | 本文件。定義 AI Agent 修改專案時必須遵守的規範 |

### 原始碼 (`src/trading/`)

| 目錄 | 用途 |
|------|------|
| `core/` | 共用基礎設施（設定、訊號偵測、回測引擎、成交模型回測引擎、資料擷取、結果儲存） |
| `experiments/_template/` | 新實驗模板，複製即可快速建立新策略 |
| `experiments/<name>/` | 各交易策略實驗，每個實驗包含 `config.py`、`signal_detector.py`、`strategy.py`，部分含自訂 `backtester.py` |

> 各實驗的詳細說明請參考 `README.md` 的「範例參照」表與 `src/trading/experiments/EXPERIMENTS_TQQQ.md`。

### 設定與 CI/CD

| 檔案 | 用途 |
|------|------|
| `pyproject.toml` | Python 專案設定，定義依賴、建置系統與 CLI 入口 |
| `.github/workflows/tqqq-backtest.yml` | GitHub Actions 工作流程，可手動觸發執行指定實驗的回測 |

## 4. 人類專用文件規範

- **強調**：`HUMAN_PM_MEMO.md` 是專門讓人類來寫的。
- **權限限制**：AI Agent 除非是自稱（或被明確指定為） `HUMAN_PM_HELPER`，否則**不可以**更動此檔案。
