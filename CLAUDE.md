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

- **Workflow-first research**：新的 outcome-relevant 研究 identity 必須由 released workflow
  與其 study 治理。第一次會影響選擇的正式 execution 或 outcome inspection 前，study 必須
  preregister；純工程維護與不查看 outcome 的探索不需要 study。
- **Versioned policies**：workflow 必須明確選擇 released market、broker、execution 與
  portfolio policy versions，不可使用隱含 latest 或複製後自行覆寫。
- **Legacy identity freeze**：`src/trading/experiments/` 是封閉的 legacy inventory。不得新增、
  改名或就地改變既有 identity 的研究語意；改良必須建立 workflow-native research definition。

- **程式碼與文件同步**：任何程式碼變更都必須同步更新相關文件，確保文件準確反映實際行為。
- **架構文件是唯一權威**：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 是專案檔案、資料夾用途與 ownership boundary 的 canonical map。
- **自動維護架構文件**：新增、刪除、搬移、重新命名或改變 tracked 檔案／資料夾用途時，必須在同一個 change 更新 `docs/ARCHITECTURE.md`。新增 public entry point、重複性檔案模式、generated artifact 或 local-only data boundary 時亦同。若只是新增符合文件既有 pattern 的 experiment、result、test、ADR 或 workflow study，無須逐一列出，除非 pattern 或責任本身改變。
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

# 尚未完成 Phase 9 migration 的實驗必須明確選擇 legacy historical run；不會更新 latest.json
uv run trading run <experiment_name> --legacy

# Phase 9 parity-linked migration evidence；只寫 immutable historical envelope，不更新 latest/qualification/lifecycle
uv run trading run <experiment_name> --offline results/<experiment>/<snapshot_id>.snapshot.json \
  --migration-parity results/<experiment>/<snapshot_id>.migration-parity.json

# 比較實驗結果
uv run trading compare <exp1> <exp2>

# 產生跟單訊號報告（Firstrade 下單用）
uv run trading followup

# 初始化、驗證、成交事件與 broker reconciliation（Phase 5 dry-run）
uv run trading ledger init --managed-capital 100000 --universe \
  CIBR COPX DIA EEM EWJ EWT EWZ FCX FXI GLD INDA IWM NVDA SIVR SOXL SPY \
  TLT TQQQ TSLA TSM URA USO VGK VOO XBI XLU
uv run trading ledger verify
uv run trading ledger record --event-type deposit --amount 1000
uv run trading ledger allocate --allocation-epoch epoch-0002 \
  --sleeve-capital SPY=50000 QQQ=40000 --reserve-cash 10000
uv run trading ledger reconcile --broker-export broker-imports/account.csv
uv run trading ledger export backup/manual-execution-ledger.csv
uv run trading ledger import backup/manual-execution-ledger.csv --path state/manual-execution-ledger.csv

# 唯讀檢查 Phase 6 Historical / Shadow lifecycle（不執行、不授權 live trading）
uv run trading qualification status

# 註冊 forward-only qualification plan；created_at 固定取當下 UTC，不接受回填
uv run trading qualification plan register --help

# 最後一個 frozen fold 完成後，以每個 family trial 的 exact manifest 重算 screen
uv run trading qualification screen run --help

# Phase 7 controlled cutover（預設 no-new-entry；仍為 dry-run）
uv run trading followup-state init
uv run trading followup-state status
uv run trading followup-state pause --reason "operator rollback"
# Active promotion additionally requires exact Shadow, activation, result, and parity identities.
uv run trading followup-state activate --help

# Phase 8 private drift evidence (dry-run only; no broker access)
uv run trading drift status --path state/live-drift/<strategy>.json
uv run trading drift checkpoint --help
uv run trading drift recover --help

# 回測目前跟單策略組合（預設最近 126 個完整交易日）
uv run trading followup-backtest

# 自訂完整交易日數
uv run trading followup-backtest --days 180

# 從指定日期當天或之後第一個完整交易日起，回測 126 個交易日
uv run trading followup-backtest --start 2025-01-01 --days 126

# 檢查知識新鮮度
uv run trading freshness

# 唯讀驗證所有 tracked workflow metadata、索引與 immutable evidence
uv run trading workflow validate --all

# 驗證／同步 versioned executable policy registry
uv run trading policy validate --all
uv run trading policy sync

# 從 metadata 重建 root 與 version README 索引
uv run trading workflow sync

# 依合法生命週期轉換 workflow change 或 version
uv run trading workflow change transition <change-path> --to proposed
uv run trading workflow version transition <version-path> --to retired \
  --approved-by <human-id>

# 準備經人類批准的 workflow release；合併 canonical branch 後才生效
uv run trading workflow release <version-path> --approved-by <human-id>

# 在 active workflow version 下建立並預註冊 study；時間固定取當下 UTC
uv run trading workflow study init <version-path> --slug <study-slug> \
  --title <title> --created-by <identity>
uv run trading workflow study preregister <study-path> --approved-by <human-id>

# 依 frozen plan 推進 study；pause/cancel 必須附 reason
uv run trading workflow study transition <study-path> --to running --by <identity>
uv run trading workflow study transition <study-path> --to awaiting-review --by <identity>

# 獨立 reviewer 確認後凍結 evidence、conclusion 與 outcome
uv run trading workflow study complete <study-path> \
  --outcome <pass|fail|insufficient-evidence|indeterminate> --reviewed-by <identity>

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

# 唯讀檢查 result validity；不 refresh、不寫入結果
uv run trading result status <experiment_name>
uv run trading result status --all

# 明確評估單一資產；先處理全部 stale candidates，無法完整更新則不排名
uv run trading result evaluate <asset>

# 一次性建立 legacy experiment inventory；會明確標記 selection history incomplete
uv run trading result registry seed
```

## 架構速覽

[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 是 repository structure、各檔案／資料夾用途、
tracked evidence 與 local-only runtime boundary 的唯一權威。需要找實作位置或調整檔案結構時先查閱該文件；
不要在本文件維護第二份容易分歧的完整 tree。

Phase 5 manual-execution details and the broker-export CSV contract are documented in
[docs/manual-execution-ledger.md](docs/manual-execution-ledger.md). Runtime ledger, reconciliation,
broker-import, and credential files are local-only and must remain outside Git.

Phase 6 historical qualification, benchmark, selection-adjustment, Shadow, and local registry
contracts are documented in
[docs/historical-qualification-and-shadow.md](docs/historical-qualification-and-shadow.md).

Phase 7 controlled-cutover lifecycle, no-new-entry rollback, Active authorization, migration parity,
and allocation-epoch contracts are documented in
[docs/controlled-followup-cutover.md](docs/controlled-followup-cutover.md).

Phase 8 frozen predictive drift envelopes, Healthy/Watch/Paused overlay, hard guards, deterministic
checkpoints, and fail-closed recovery contracts are documented in
[docs/live-drift-and-recovery.md](docs/live-drift-and-recovery.md). The registry is private under
`state/live-drift/`; never commit its events, ledger exports, credentials, or personal trading data.

## 按需參考（不需要時不用讀）

- 建立新實驗教學 → [README.md](README.md)
- Versioned executable policies → [docs/policies.md](docs/policies.md)
- 專案檔案與資料夾用途 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 資產實驗總覽 → `src/trading/experiments/EXPERIMENTS_<TICKER>.md`（例如 [TQQQ](src/trading/experiments/EXPERIMENTS_TQQQ.md)、[GLD](src/trading/experiments/EXPERIMENTS_GLD.md)）
- 成交模型完整規格 → [.agents/rules/execution-model.md](.agents/rules/execution-model.md)
- 跨資產共通教訓 → [.agents/context/cross_asset_lessons.md](.agents/context/cross_asset_lessons.md)
- 跨資產詳細證據 → [.agents/context/cross_asset_evidence.md](.agents/context/cross_asset_evidence.md)
