# AI Agent 工作規範

## 1. 程式碼與文件一致性

AI Agent 在修改專案時，必須確保程式碼與文件保持同步：

- **新增或修改功能時**：同步更新相關文件（如 `README.md`、API 文件、註解等），使其準確反映最新的程式碼行為。
- **刪除功能時**：移除文件中對應的描述，避免留下過時或誤導性的內容。
- **修改設定或參數時**：更新文件中的設定說明、範例與預設值。
- **變更檔案結構時**：更新文件中的目錄結構說明與檔案路徑參照。

> 任何程式碼的變更都不應導致文件與實際行為不一致。若發現既有的不一致，應主動修正。

## 2. 專案檔案用途說明

### 根目錄文件

| 檔案 | 用途 |
|------|------|
| `README.md` | 專案總覽、架構說明、快速開始指南、新實驗建立教學 |
| `MEMO.md` | 研究備忘錄，記錄關注標的與未來研究方向 |
| `PLAN_TQQQ_NEXT.md` | TQQQ 下一階段實驗規劃，包含 TQQQ-005/006/007 的設計與評估標準 |
| `pyproject.toml` | Python 專案設定，定義依賴、建置系統與 CLI 入口 (`trading`) |
| `uv.lock` | uv 套件管理器的鎖定檔，確保依賴版本一致性 |
| `.python-version` | Python 版本指定檔 |
| `.gitignore` | Git 忽略規則，排除快取、虛擬環境、實驗結果等 |

### 原始碼 (`src/trading/`)

| 檔案 / 目錄 | 用途 |
|-------------|------|
| `__init__.py` | 套件入口，提供 `main()` 函式作為主程式進入點 |
| `cli.py` | 統一 CLI 入口，支援 `list` / `run` / `compare` 子命令 |
| `core/` | 共用基礎設施（設定、訊號偵測、回測引擎、資料擷取、結果儲存） |
| `experiments/` | 所有交易策略實驗的存放目錄 |
| `experiments/__init__.py` | 實驗註冊表，管理所有實驗的載入與查詢 |
| `experiments/_template/` | 新實驗模板，複製即可快速建立新策略 |
| `experiments/tqqq_capitulation/` | TQQQ-001：基礎恐慌抄底策略（當前基線） |
| `experiments/tqqq_cap_relaxed_entry/` | TQQQ-002：放寬進場條件變體 |
| `experiments/tqqq_cap_wider_exit/` | TQQQ-003：放寬出場條件 + 追蹤停利變體 |
| `experiments/tqqq_cap_vix_filter/` | TQQQ-004：VIX 過濾器變體 |
| `experiments/tqqq_cap_vix_adaptive/` | TQQQ-005：軟性 VIX + 適應性出場變體 |

### CI/CD

| 檔案 | 用途 |
|------|------|
| `.github/workflows/tqqq-backtest.yml` | GitHub Actions 工作流程，可手動觸發執行指定實驗的回測 |

### AI Agent 規範

| 檔案 | 用途 |
|------|------|
| `.agents/rules/ai-agent-guidelines.md` | 本文件。定義 AI Agent 修改專案時必須遵守的規範 |
| `CLAUDE.md` | Claude Code 的專案規則入口，指引 AI 遵循本規範 |
