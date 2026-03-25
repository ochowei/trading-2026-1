# AI Agent 工作規範

## 1. 程式碼與文件一致性

AI Agent 在修改專案時，必須確保程式碼與文件保持同步：

- **新增或修改功能時**：同步更新相關文件（如 `README.md`、API 文件、註解等），使其準確反映最新的程式碼行為。
- **刪除功能時**：移除文件中對應的描述，避免留下過時或誤導性的內容。
- **修改設定或參數時**：更新文件中的設定說明、範例與預設值。
- **變更檔案結構時**：更新文件中的目錄結構說明與檔案路徑參照。

> 任何程式碼的變更都不應導致文件與實際行為不一致。若發現既有的不一致，應主動修正。

## 2. 專案檔案用途說明

### 文件類（Markdown）

| 檔案 | 用途 |
|------|------|
| `README.md` | 專案總覽、架構說明、快速開始指南、新實驗建立教學 |
| `MEMO.md` | 研究備忘錄，記錄關注標的與未來研究方向 |
| `CLAUDE.md` | Claude Code 的專案規則入口，指引 AI 遵循本規範 |
| `.agents/rules/ai-agent-guidelines.md` | 本文件。定義 AI Agent 修改專案時必須遵守的規範 |

### 原始碼 (`src/trading/`)

| 目錄 | 用途 |
|------|------|
| `core/` | 共用基礎設施（設定、訊號偵測、回測引擎、資料擷取、結果儲存） |
| `experiments/_template/` | 新實驗模板，複製即可快速建立新策略 |
| `experiments/<name>/` | 各交易策略實驗，每個實驗包含 `config.py`、`signal_detector.py`、`strategy.py`，部分含自訂 `backtester.py` |

> 各實驗的詳細說明請參考 `README.md` 的「範例參照」表與 `src/trading/experiments/EXPERIMENTS_TQQQ.md`。

### 設定與 CI/CD

| 檔案 | 用途 |
|------|------|
| `pyproject.toml` | Python 專案設定，定義依賴、建置系統與 CLI 入口 |
| `.github/workflows/tqqq-backtest.yml` | GitHub Actions 工作流程，可手動觸發執行指定實驗的回測 |
