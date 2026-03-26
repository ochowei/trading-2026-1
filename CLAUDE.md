# CLAUDE.md

## 規則（必讀）

- **程式碼與文件同步**：任何程式碼變更都必須同步更新相關文件，確保文件準確反映實際行為。
- **檔案結構變更**：新增、刪除或搬移檔案時，必須更新本文件的「架構速覽」段落。
- **新增實驗時**：更新 `.github/workflows/tqqq-backtest.yml` 的實驗選項、`EXPERIMENTS_TQQQ.md` 或 `EXPERIMENTS_GLD.md`。
- **發現不一致時**：主動修正文件與程式碼之間的不一致。
- **人類專用文件**：`HUMAN_PM_MEMO.md` 由人類維護，AI Agent 除非被明確指定為 `HUMAN_PM_HELPER`，否則不可編輯。

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
```

## 架構速覽

```
src/trading/
├── cli.py                       # 統一 CLI 入口
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
- 成交模型完整規格 → [.agents/rules/execution-model.md](.agents/rules/execution-model.md)
