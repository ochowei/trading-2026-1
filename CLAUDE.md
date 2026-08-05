# CLAUDE.md

## AI Agent 讀取策略（節省 token）

設計新實驗時，按以下順序讀取，夠用就停：
1. **先讀** [.agents/context/cross_asset_lessons.md](.agents/context/cross_asset_lessons.md) 的跨資產共通教訓（精簡規則版，~290 行）
1b. **檢查新鮮度**：若任何教訓的 `data_through` 距今超過 6 個月，在實驗提案中標註「基於較舊數據，建議先重新驗證」
2. **再讀** EXPERIMENTS_*.md 的 `AI Agent 快速索引` 區塊
3. **再讀** 參數對照表（Parameter Comparison）
4. **需要特定規則的詳細證據時**，讀 [.agents/context/cross_asset_evidence.md](.agents/context/cross_asset_evidence.md) 的對應段落（不要整份讀）
5. **只有需要了解實作細節時**，才讀個別實驗的 config.py / signal_detector.py
6. **不需要** 讀每個實驗的完整程式碼，mdoc 已包含關鍵參數

## 規則（必讀）

- **程式碼與文件同步**：任何程式碼變更都必須同步更新相關文件，確保文件準確反映實際行為。
- **檔案結構變更**：新增、刪除或搬移檔案時，必須更新本文件的「架構速覽」段落。
- **新增實驗時**：更新 `.github/workflows/tqqq-backtest.yml` 的實驗選項，以及對應資產的 `src/trading/experiments/EXPERIMENTS_<TICKER>.md`。若是全新資產，建立該總覽文件並在本文件的「按需參考」保留通用查找方式，不要新增逐一列舉且容易過期的資產清單。
- **更新 EXPERIMENTS_*.md 時**：AI Agent 必須同時維護並更新各個 `EXPERIMENTS_*.md` 檔案最頂端的 AI Agent 專用摘要區塊（`<!-- AI_CONTEXT_START ... -->`），確保快速索引（當前最佳、已證明無效、參數空間、未嘗試方向等）保持在最新狀態。
- **知識新鮮度**：更新 EXPERIMENTS_*.md 的 AI_CONTEXT 或 cross_asset_lessons.md 時，同步更新 `validated` 和 `data_through` 日期。
- **發現不一致時**：主動修正文件與程式碼之間的不一致。
- **人類專用文件**：`pm/` 資料夾由人類維護，AI Agent 除非被明確指定為 `HUMAN_PM_HELPER`，否則不可編輯其中的任何文件。

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

# 執行已 prepare 的 snapshot-aware 實驗（預設 formal online）
uv run trading run <experiment_name>

# 尚未完成 Phase 9 migration 的實驗必須明確選擇 legacy persisted run
uv run trading run <experiment_name> --legacy

# 比較實驗結果
uv run trading compare <exp1> <exp2>

# 產生跟單訊號報告（Firstrade 下單用）
uv run trading followup

# 回測目前跟單策略組合（預設最近 126 個完整交易日）
uv run trading followup-backtest

# 自訂完整交易日數
uv run trading followup-backtest --days 180

# 從指定日期當天或之後第一個完整交易日起，回測 126 個交易日
uv run trading followup-backtest --start 2025-01-01 --days 126

# 檢查知識新鮮度
uv run trading freshness

# 唯讀檢查單一 Yahoo adjusted daily series 的 CSV cache 狀態
uv run trading data status SPY

# 明確執行日常 incremental refresh（包含保守 overlap）
uv run trading data refresh SPY --start 2020-01-01

# 完整歷史 refresh；建立 snapshot 前必須執行
uv run trading data refresh SPY --full

# 完整刷新並捕捉 experiment definition；發布 immutable results/NAME/<snapshot_id>.snapshot.json
uv run trading data snapshot SPY --experiment <experiment_name> --aux '^VIX' \
  --history-start 2020-01-01 --decision 2026-08-04

# 不供 formal execution 的 data-only snapshot 必須指定可追蹤 destination
uv run trading data snapshot SPY --aux '^VIX' --history-start 2020-01-01 \
  --decision 2026-08-04 --manifest results/example/data.snapshot.json

# 唯讀驗證 manifest、data blob 與 definition blob
uv run trading data verify results/example/data.snapshot.json

# 匯出／匯入 portable snapshot bundle
uv run trading data export results/example/run.snapshot.json backup.snapshot.zip
uv run trading data import backup.snapshot.zip --manifest results/example/imported.snapshot.json

# Reference-aware GC 預設掃描完整 results/；額外 roots 為 additive；預設 dry-run
uv run trading data gc --grace-days 7

# Diagnostic run 不改變 results 或 registry state
uv run trading run <experiment_name> --ephemeral
```

## 架構速覽

```
CONTEXT.md                       # 量化研究領域術語與統一語言

.agents/
├── context/
│   ├── cross_asset_lessons.md   # 跨資產共通教訓（波動率分類、禁忌、參數縮放）
│   └── cross_asset_evidence.md  # 共通教訓的詳細回測證據與原因分析
├── skills/                      # Repo 專屬 Codex skills，統一使用 trading- 前綴
│   └── trading-*/
│       ├── SKILL.md
│       └── agents/openai.yaml
└── rules/
    └── execution-model.md       # 成交模型完整規格

pm/                              # 人類 PM 專用文件（AI Agent 禁止編輯）
├── HUMAN_PM_MEMO.md             # 關注標的、策略想法、執行模型備忘、更新紀錄
└── USE_CASES.md                 # 人類使用情境與常用操作索引

docs/
├── adr/                         # 架構決策紀錄（ADR）
├── market-data.md               # Phase 1 CSV cache、provider、驗證與 CLI 契約
├── reproducibility.md           # Phase 2 blobs、manifests、definitions、bundles、run modes、GC
└── superpowers/plans/           # 已確認的實作計畫

results/                         # 各實驗最新與歷史回測結果（JSON）
tests/                           # 共用引擎與 followup 行為測試

src/trading/
├── cli.py                       # 統一 CLI 入口
├── followup.py                  # 跟單訊號產生器（60 天回測 + Firstrade 下單指令）
├── followup_backtest.py         # 跟單策略等權袖套回測、每日 equity 與結構化報告
├── core/                        # 共用基礎設施
│   ├── base_config.py           # ExperimentConfig dataclass
│   ├── base_signal_detector.py  # BaseSignalDetector ABC
│   ├── base_backtester.py       # 通用回測引擎（停利/停損/到期）
│   ├── execution_backtester.py  # 成交模型回測引擎（滑價/悲觀認定/隔日開盤）
│   ├── base_strategy.py         # BaseStrategy（fetch → 指標 → 訊號 → 回測 → 報表）
│   ├── execution_strategy.py    # ExecutionModelStrategy（成交模型報表）
│   ├── data_fetcher.py          # 相容層：多 ticker 存取 validated CSV market data
│   ├── performance_analyzer.py  # 滾動窗口績效與漸變性分析
│   ├── freshness.py             # 知識新鮮度檢查（data_through 過期掃描）
│   ├── results.py               # 結果儲存（JSON）與跨實驗比較
│   └── sync_docs.py             # Markdown 結果與 latest.json 同步檢查
├── market_data/                 # Yahoo adjusted daily provider boundary 與 CSV cache
│   ├── contracts.py             # Calendar/reader protocols 與 RefreshKind vocabulary
│   ├── models.py                # Series/requirement/policy/decision/metadata value types
│   ├── provider.py              # 外部 provider protocol 與 Yahoo adapter
│   ├── calendar.py              # XNYS sessions、特殊休市與 actual-close cutoff
│   ├── validation.py            # OHLCV/schema/session fail-closed validation
│   ├── cache.py                 # Lock、canonical CSV、sidecar、atomic publish、quarantine
│   ├── service.py               # Fresh reuse、incremental/full refresh orchestration
│   └── bundle.py                # Read-only bundle 與 backward as-of auxiliary alignment
├── research_data/               # Phase 2 immutable reproducibility evidence
│   ├── artifacts.py             # 共用 immutable publish/checksum/semantic verification
│   ├── manifest_codec.py        # 嚴格型別、canonical manifest codec 與 snapshot identity
│   ├── models.py                # Blob/manifest/definition/run/GC immutable values
│   ├── store.py                 # Snapshot orchestration、portable bundles、verification、GC
│   ├── definitions.py           # Semantic fingerprint 與 dirty-worktree definition blobs
│   └── runs.py                  # Online/offline/ephemeral publication boundaries
└── experiments/                 # 各實驗（pkgutil 自動發現，無需手動註冊）
    ├── _template/               # 新實驗模板（複製即用）
    ├── EXPERIMENTS_<TICKER>.md  # 各資產實驗總覽與 AI_CONTEXT
    └── <name>/                  # config.py + signal_detector.py + strategy.py + __init__.py
```

## 按需參考（不需要時不用讀）

- 建立新實驗教學 → [README.md](README.md)
- 資產實驗總覽 → `src/trading/experiments/EXPERIMENTS_<TICKER>.md`（例如 [TQQQ](src/trading/experiments/EXPERIMENTS_TQQQ.md)、[GLD](src/trading/experiments/EXPERIMENTS_GLD.md)）
- 成交模型完整規格 → [.agents/rules/execution-model.md](.agents/rules/execution-model.md)
- 跨資產共通教訓 → [.agents/context/cross_asset_lessons.md](.agents/context/cross_asset_lessons.md)
- 跨資產詳細證據 → [.agents/context/cross_asset_evidence.md](.agents/context/cross_asset_evidence.md)
