# CLAUDE.md

## AI Agent 讀取策略（節省 token）

設計新的 workflow-native research definition／trial 時，按以下順序讀取，夠用就停：
1. **先讀** [.agents/context/cross_asset_lessons.md](.agents/context/cross_asset_lessons.md) 的跨資產共通教訓（精簡規則版，~290 行）
1b. **檢查新鮮度**：若任何教訓的 `data_through` 距今超過 6 個月，在實驗提案中標註「基於較舊數據，建議先重新驗證」
2. **需要歷史脈絡時**，再讀 `legacy/experiment-overviews/EXPERIMENTS_*.md` 的
   `AI Agent 快速索引` 區塊；它是 legacy evidence，不是新研究 authority
3. **需要 legacy 參數脈絡時**，再讀參數對照表（Parameter Comparison）
4. **需要特定規則的詳細證據時**，讀 [.agents/context/cross_asset_evidence.md](.agents/context/cross_asset_evidence.md) 的對應段落（不要整份讀）
5. **只有需要了解實作細節時**，才讀個別實驗的 config.py / signal_detector.py
6. **不需要** 讀每個實驗的完整程式碼，mdoc 已包含關鍵參數

## 規則（必讀）

- **Workflow-first research**：新的 outcome-relevant 研究 identity 必須由 released workflow
  與其 study 治理。第一次會影響選擇的正式 execution 或 outcome inspection 前，study 必須
  preregister；純工程維護與不查看 outcome 的探索不需要 study。
- **Versioned policies**：workflow 必須明確選擇 released market、broker、execution 與
  portfolio policy versions，不可使用隱含 latest 或複製後自行覆寫。
- **Legacy identity freeze**：`legacy/experiments/` 是封閉的 legacy inventory；
  `src/trading/experiments/` 只是 historical import compatibility facade。不得新增、改名或就地
  改變既有 identity 的研究語意；改良必須建立 workflow-native research definition。

- **程式碼與文件同步**：任何程式碼變更都必須同步更新相關文件，確保文件準確反映實際行為。
- **架構文件是唯一權威**：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 是專案檔案、資料夾用途與 ownership boundary 的 canonical map。
- **自動維護架構文件**：新增、刪除、搬移、重新命名或改變 tracked 檔案／資料夾用途時，必須在同一個 change 更新 `docs/ARCHITECTURE.md`。新增 public entry point、重複性檔案模式、generated artifact 或 local-only data boundary 時亦同。若只是新增符合文件既有 pattern 的 experiment、result、test、ADR 或 workflow study，無須逐一列出，除非 pattern 或責任本身改變。
- **更新 legacy overview 時**：只有明確的 archive-maintenance 工作才可更新
  `legacy/experiment-overviews/EXPERIMENTS_*.md`，並須同步維護頂端的 `AI_CONTEXT`；新研究不更新
  legacy overview，而是在 workflow study 中保存 evidence。
- **知識新鮮度**：更新 legacy overview 的 AI_CONTEXT 或 cross_asset_lessons.md 時，同步更新
  `validated` 和 `data_through` 日期。
- **發現不一致時**：主動修正文件與程式碼之間的不一致。
- **人類專用文件**：`docs/pm/` 資料夾由人類維護，AI Agent 除非被明確指定為 `HUMAN_PM_HELPER`，否則不可編輯其中的任何文件。

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

# 日常與 PR fast regression；包含固定 legacy smoke matrix
uv run pytest -m "not slow"

# 只有 legacy/shared runtime 變更、main/release 驗證才執行完整 legacy matrix
uv run pytest -m legacy_conformance -n auto

# 一鍵修正可自動修復的問題
uv run ruff check src/ --fix && uv run ruff format src/
```

> CI（GitHub Action `ci.yml`）會在 pull request 與 `main` push 執行上述檢查，並驗證
> fast regression、workflow、policy、path ownership、legacy experiment inventory 與
> market-data boundary contracts。高風險路徑、main 與每日排程另執行完整 legacy
> conformance matrix。是否阻擋
> merge 由 GitHub branch protection 設定決定。

## 成交模型（新實驗必讀）

TQQQ-001 ~ TQQQ-009 為既往不咎實驗，可維持原始回測邏輯。所有新建實驗必須納入成交模型（進場/出場模式、未成交處理、成交統計、日內路徑假設）。完整規格見 [.agents/rules/execution-model.md](.agents/rules/execution-model.md)。該路徑已被 released workflow 固定，視為 frozen dependency；未來規則變更必須建立 versioned successor，並由新的 workflow version 明確採用，不得就地改寫。

## 開發指令

```bash
# 安裝依賴
uv sync

# 唯讀列出封存的 legacy experiment inventory
uv run trading legacy list

# Legacy experiment execution、analysis、evaluation、snapshot preparation 與 result publication
# 已正式退役並 fail closed；新研究只使用下方 trading research commands。
# 唯讀比較封存結果
uv run trading legacy compare <exp1> <exp2>

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

# 註冊 workflow-native forward-only qualification plan；created_at 固定取當下 UTC，不接受回填
uv run trading qualification plan register --research <family/trial> \
  --workflow <released-version-path> --dry-run
# --experiment 僅保留 parser/API compatibility，永遠在任何 registry、lock 或 evidence 寫入前 fail closed
# Capability-scoped workflow study 一律由 exact frozen study 編譯；dry-run 不寫 registry
uv run trading qualification plan register-study --study <study-path> --dry-run

# 最後一個 frozen fold 完成後，以每個 family trial 的 exact manifest 重算 screen
uv run trading qualification screen run --help

# Phase 7 legacy followup 只保留 no-new-entry、狀態查詢與既有部位退役
uv run trading followup-state status
uv run trading followup-state pause --reason "operator rollback"
uv run trading followup-state retire --help
uv run trading followup-state complete-retirement --help

# Phase 8 private drift evidence (dry-run only; no broker access)
uv run trading drift status --path state/live-drift/<strategy>.json
uv run trading drift checkpoint --help
uv run trading drift recover --help

# 聚合檢查 active knowledge 與明確標示的 legacy archive freshness
uv run trading freshness
# 只檢查 legacy overview 與 archived result validity
uv run trading legacy freshness

# 唯讀驗證所有 tracked workflow metadata、索引與 immutable evidence
uv run trading workflow validate --all

# 驗證／同步 versioned executable policy registry
uv run trading policy validate --all
uv run trading policy sync

# 從 metadata 重建 root 與 version README 索引
uv run trading workflow sync

# 高階 authoring façade：request JSON 不配置 ID/status/timestamp；先 dry-run 再套用
uv run trading workflow create --request authoring-request.json --dry-run
uv run trading workflow change create --request change-request.json --dry-run
uv run trading workflow evolve --request evolve-request.json --dry-run
# 人類確認 preview 後，移除 --dry-run 執行同一 request；decision/release 仍使用下列獨立命令
# façade 只讀且預設保留 request 與來源文件；move/pointer/remove 是另一次 exact-path 人類確認

# 低階 compatibility/diagnostic seam：依既有 guard 轉換 change/version，不取代上述 authoring happy path
uv run trading workflow change transition <change-path> --to proposed
uv run trading workflow version transition <version-path> --to retired \
  --approved-by <human-id>

# 獨立 human-authority seam：準備 release；合併 canonical branch 後才生效
uv run trading workflow release <version-path> --approved-by <human-id>

# 在 active workflow version 下建立並預註冊 study；時間固定取當下 UTC
uv run trading workflow study init <version-path> --slug <study-slug> \
  --title <title> --created-by <identity> \
  --route <clean-historical|retrospective-confirmatory|study-time-retrospective>
uv run trading workflow study preregister <study-path> --approved-by <human-id>

# 依 frozen plan 推進 study；首次 Development 另需 human stage approval；pause/cancel 必須附 reason
uv run trading workflow study transition <study-path> --to running --by <identity> \
  --approved-by <human-id>
# Development selection JSON contains only selected_candidate, family_baseline, and complete_family;
# guarded writer adds current-time approval and exact frozen study identities add-only.
uv run trading workflow study freeze-candidate <study-path> \
  --selection <development-selection.json> --approved-by <human-id>
uv run trading workflow study transition <study-path> --to awaiting-review --by <identity>

# 獨立 reviewer 確認後凍結 evidence、conclusion 與 outcome
uv run trading workflow study complete <study-path> \
  --outcome <pass|fail|insufficient-evidence|indeterminate> --reviewed-by <identity>

# 列出、捕捉與正式執行 workflow-native research definitions；不經 legacy registry
uv run trading research list
uv run trading research snapshot <family/trial> --workflow <released-version-path> \
  --decision 2026-08-04
# 同一 cutoff 的 family trials 共用首個已完成的 full-refresh generation；此模式不呼叫 provider，
# 並由 snapshot eligibility 驗證 full-refresh freshness、coverage 與 exact cutoff
uv run trading research snapshot <family/trial> --workflow <released-version-path> \
  --decision 2026-08-04 --reuse-full-refresh
uv run trading research run <family/trial> --workflow <released-version-path> \
  --manifest results/<result-name>/<snapshot-id>.snapshot.json --offline

# 唯讀檢查單一 Yahoo adjusted daily series 的 CSV cache 狀態
uv run trading data status SPY

# 明確執行日常 incremental refresh（包含保守 overlap）
uv run trading data refresh SPY --start 2020-01-01

# 完整歷史 refresh；建立 snapshot 前必須執行
uv run trading data refresh SPY --full

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

# 唯讀檢查封存的 legacy result；不 refresh、不寫入結果
uv run trading legacy result status <experiment_name>
uv run trading legacy result status --all
```

舊的頂層 `trading list`、`compare`、`result status`、`run`、`analyze`、`sync-docs` 與
`followup-backtest` 已移除並由 argparse 拒絕。唯讀 legacy diagnostics 與明確的 retired
fail-closed entry 只存在於 `trading legacy ...`。

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

- 建立 workflow-native research definition／trial 的入口 → [README.md](README.md)
- 文件狀態與被 pin 住的舊命令說明 → [docs/README.md](docs/README.md)
- Versioned executable policies → [docs/policies.md](docs/policies.md)
- 專案檔案與資料夾用途 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Legacy 資產實驗總覽 → `legacy/experiment-overviews/EXPERIMENTS_<TICKER>.md`（例如 [TQQQ](legacy/experiment-overviews/EXPERIMENTS_TQQQ.md)、[GLD](legacy/experiment-overviews/EXPERIMENTS_GLD.md)）；僅供歷史脈絡，不是 workflow outcome authority
- 成交模型完整規格 → [.agents/rules/execution-model.md](.agents/rules/execution-model.md)
- 跨資產共通教訓 → [.agents/context/cross_asset_lessons.md](.agents/context/cross_asset_lessons.md)
- 跨資產詳細證據 → [.agents/context/cross_asset_evidence.md](.agents/context/cross_asset_evidence.md)
