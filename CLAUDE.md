# CLAUDE.md

## 規則（必讀）

- **程式碼與文件同步**：任何程式碼變更都必須同步更新相關文件，確保文件準確反映實際行為。
- **檔案結構變更**：新增、刪除或搬移檔案時，必須更新本文件的「架構速覽」段落。
- **新增實驗時**：更新 `.github/workflows/tqqq-backtest.yml` 的實驗選項、`EXPERIMENTS_TQQQ.md`、`EXPERIMENTS_GLD.md` 或 `EXPERIMENTS_SIVR.md`。
- **發現不一致時**：主動修正文件與程式碼之間的不一致。
- **人類專用文件**：`HUMAN_PM_MEMO.md` 由人類維護，AI Agent 除非被明確指定為 `HUMAN_PM_HELPER`，否則不可編輯。

## 程式碼風格（必讀）

本專案使用 **Ruff** 統一 lint 與格式化，所有新增或修改的 Python 程式碼必須符合以下規則。

### 撰寫前確認

- **不寫多餘的 f-string**：字串中沒有 `{}` 佔位符時，直接用 `"..."` 而非 `f"..."`。
- **不留未使用的 import**：只 import 實際用到的名稱，移除多餘的 import。
- **不留未使用的變數**：若計算結果不需要保留，不要賦值給變數（或直接省略該行）。
- **import 順序**：標準庫 → 第三方套件 → 本地模組，各組之間空一行（isort 規則）。
- **使用新式語法**：Python 3.11+ 可用的語法優先（例如 `X | Y` 取代 `Optional[X]`）。

### 撰寫後驗證

完成程式碼後，執行以下指令確認通過再提交：

```bash
# 安裝 dev 依賴（第一次需要）
uv sync --group dev

# 檢查 lint（必須 0 errors）
uv run ruff check src/

# 檢查格式（必須 0 files would be reformatted）
uv run ruff format --check src/

# 一鍵修正可自動修復的問題
uv run ruff check src/ --fix && uv run ruff format src/
```

> CI（GitHub Action `lint.yml`）會在每次 push / PR 自動執行上述檢查，未通過則 block merge。

## 成交模型（新實驗必讀）

TQQQ-001 ~ TQQQ-009 為既往不咎實驗，可維持原始回測邏輯。所有新建實驗必須納入成交模型（進場/出場模式、未成交處理、成交統計、日內路徑假設）。完整規格見 [.agents/rules/execution-model.md](.agents/rules/execution-model.md)。

## 開發指令

```bash
# 安裝依賴
uv sync

# 列出所有實驗
uv run trading list

# 執行指定實驗
uv run trading run <experiment_name>

# 比較實驗結果
uv run trading compare <exp1> <exp2>

# 產生跟單訊號報告（Firstrade 下單用）
uv run trading followup
```

## 架構速覽

```
src/trading/
├── cli.py                       # 統一 CLI 入口
├── followup.py                  # 跟單訊號產生器（60 天回測 + Firstrade 下單指令）
├── core/                        # 共用基礎設施
│   ├── base_config.py           # ExperimentConfig dataclass
│   ├── base_signal_detector.py  # BaseSignalDetector ABC
│   ├── base_backtester.py       # 通用回測引擎（停利/停損/到期）
│   ├── execution_backtester.py  # 成交模型回測引擎（滑價/悲觀認定/隔日開盤）
│   ├── base_strategy.py         # BaseStrategy（fetch → 指標 → 訊號 → 回測 → 報表）
│   ├── execution_strategy.py    # ExecutionModelStrategy（成交模型報表）
│   ├── data_fetcher.py          # yfinance 多線程資料抓取
│   └── results.py               # 結果儲存（JSON）與跨實驗比較
└── experiments/                 # 各實驗（pkgutil 自動發現，無需手動註冊）
    ├── _template/               # 新實驗模板（複製即用）
    └── <name>/                  # config.py + signal_detector.py + strategy.py + __init__.py
```

## 按需參考（不需要時不用讀）

- 建立新實驗教學 → [README.md](README.md)
- TQQQ 實驗總覽 → [src/trading/experiments/EXPERIMENTS_TQQQ.md](src/trading/experiments/EXPERIMENTS_TQQQ.md)
- GLD 實驗總覽 → [src/trading/experiments/EXPERIMENTS_GLD.md](src/trading/experiments/EXPERIMENTS_GLD.md)
- SIVR 實驗總覽 → [src/trading/experiments/EXPERIMENTS_SIVR.md](src/trading/experiments/EXPERIMENTS_SIVR.md)
- FCX 實驗總覽 → [src/trading/experiments/EXPERIMENTS_FCX.md](src/trading/experiments/EXPERIMENTS_FCX.md)
- 成交模型完整規格 → [.agents/rules/execution-model.md](.agents/rules/execution-model.md)
