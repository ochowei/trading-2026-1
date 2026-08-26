# `results/` 導覽

這裡存放的是可重現研究的機器產物與審查 evidence，不是一份依績效排序的報告目錄。
很多檔名刻意使用 SHA-256、snapshot identity 或時間戳，目的是固定 exact bytes 與來源關係，
因此不應為了可讀性直接重新命名、搬移或手動修改既有檔案。

如果只是想知道某個 Study 最後得到什麼結論，應先讀 repository-root
[`workflows/`](../workflows/README.md) 中該 Study 的 `CONCLUSION.md`；不要從這裡的 raw result
或 snapshot 自行推斷正式 outcome。完整路徑與 ownership contract 以
[`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md#results) 為準。

## 先從目的找路徑

| 我想找的內容 | 應查看的位置 | 注意事項 |
|---|---|---|
| Study 的狀態、計畫或最終結論 | `../workflows/<workflow>--vNNN/work/studies/<study>/` | `README.md` 是狀態入口，`PLAN.md` 是 frozen plan，`CONCLUSION.md` 是獨立審查結論。 |
| Workflow-native trial 的資料與定義快照 | `research-trials/<family>/<trial>/` | `.snapshot.json` 是可重現 manifest，不等同於績效結論。 |
| 已退役 legacy experiment 的 retained result | `../legacy/results/<experiment>/` | 僅供唯讀診斷、歷史重播與既有部位退出；不再是 current authority。 |
| Study Development gate、候選選擇或 challenge evidence | `workflows/<workflow>--vNNN/<study>/<stage>/` | 這是 Study 執行 evidence；workflow 與 Study 定義仍在 repository-root `workflows/`。 |
| Snapshot migration 的 parity 與封裝結果 | `migration-evidence/<experiment>/` | 只證明 migration 關係，不會成為 current result authority。 |
| Candidate freeze 或 qualification 所引用的固定內容 | `evidence/research/`、`evidence/qualification/` | 檔名是內容雜湊；由其他 immutable record 引用。 |
| Trial identity、observation 或舊路徑的新位置 | `registries/` | Registry 是 append-only machine state，不是人工維護的索引頁。 |
| 舊 schema、舊 alias 或已歸檔歷史結果 | `../legacy/results/` | 僅供相容性診斷與歷史追查；不可作為 selection 或 qualification authority。 |

## 目錄關係

```text
人類可讀的研究治理與結論
workflows/<workflow-version>/work/studies/<study>/
    PLAN.md + PREREGISTRATION.json + COMPLETION.json + CONCLUSION.md
                         |
                         | 引用 exact evidence
                         v
results/
├── research-trials/     workflow-native trial 的 snapshots / formal run artifacts
├── workflows/           workflow Study 各 stage 的 retained evidence
├── evidence/            content-addressed supporting evidence
└── registries/          trial identity、observation 與 path migration 關係

Legacy 相容性支線
results/migration-evidence/  frozen migration parity / result envelopes
                         |
                         | digest-verified historical references
                         v
legacy/results/           全部已退役、非 current-authority 的 legacy results
```

`src/trading/research_definitions/` 是 workflow-native trial 的 source definition；
`results/research-trials/` 是其執行所固定的 artifacts。兩者不要混為一談。

## 各 namespace 的責任

### `research-trials/`

路徑 identity 是 `<family>/<trial>`，與
`src/trading/research_definitions/<family>/<trial>/definition.py` 對應。常見檔案：

- `<snapshot-id>.snapshot.json`：固定 decision time、資料 series/blob 與 definition digest 的
  immutable snapshot manifest。
- `<timestamp>_<mode>_<run-id>.json`：以該 snapshot 執行後的 formal result；是否被 Git retained
  由 repository policy 決定，不能因為本機看得到就假設它是 tracked evidence。

同一 trial 可以有多個 snapshot，通常代表不同 cutoff、資料 generation 或 definition identity。
不能以檔名排序判定哪一個是正式選用版本；應由 Study plan/evidence 或 registry observation 反查。

### 已退役的 `experiment-results/`

Legacy experiment system 已正式停止。原 `results/experiment-results/` 內容已 byte-preserving
搬到 `../legacy/results/<experiment>/`：

- `latest.json`：目前 retained pointer/result，但存在不代表仍然 valid。
- `prev_1.json`、`prev_2.json`：存在時是保留的近期前版。
- `<snapshot-id>.snapshot.json`：legacy experiment 的 reproducibility manifest。
- `<timestamp>_<online|offline>_<run-id>.json`：一次歷史執行的完整 payload。

這些檔案只供 `trading list`、`trading compare`、`trading result status` 等唯讀診斷，以及
既有部位的 fail-closed 退出相容性。`trading run`、`analyze`、`result evaluate`、legacy snapshot
preparation、registry seed 與 followup promotion 都會拒絕執行。新研究只可使用 released workflow
與 `trading research`。

### `workflows/`

路徑為 `<workflow>--vNNN/<study>/<stage>/<artifact>`，保存 Study 執行過程中必須永久保留的
gate、selection 與 challenge evidence。常見檔案：

- `development-gate.json`：Development stage 的 guarded gate evidence。
- `development-selection.json`：固定 selected candidate、family baseline 與 complete family identity。

這裡不保存 workflow 規格本身，也不是查看 Study 最終 outcome 的第一入口。規格、lifecycle、
frozen plan 與 conclusion 位於 repository-root `workflows/`。

### `evidence/`

- `evidence/research/<sha256>.md`：candidate freeze 所引用的 pre-freeze research evidence。
- `evidence/qualification/<sha256>.json`：terminal decision 或 Development absence proof 可 replay
  的 qualification registry/checkpoint snapshot。

檔名 SHA-256 是 content address。即使內容看似重複或檔名不可讀，也不能任意改名或刪除。

### `migration-evidence/`

- `<snapshot-id>.migration-parity.json`：固定 snapshot 上的新舊執行 parity 證據。
- `<snapshot-id>.migration-result.json`：引用 parity artifact 的 migration result envelope。

這些檔案只支援 migration audit；它們不會更新 `latest.json`，也不會自行授權 qualification、
promotion 或 live trading。

### `registries/`

- `trial_registry.json`：append-only family/trial identity、definition fingerprint 與 formal
  observation inventory。舊資料可能標記 `selection_history_incomplete`，不可把缺少 observation
  解讀成「從未執行」。
- `path-migrations.json`：append-only 的舊路徑到 retained path 映射，並固定 artifact class、
  migration version 與 SHA-256。

部分 frozen artifact 內仍會出現 migration 前的 `results/<old-name>/...` 路徑。這是保留原始 bytes
的正常現象；runtime reader 會透過 `path-migrations.json` 做 bounded、digest-verified resolution。
v010 只允許 v009 categorized result 再增加一個 byte-identical retirement hop 到 `legacy/results/`。
不要為了更新字串而改寫 frozen artifact。

## 檔名字典

| 形式 | 含義 |
|---|---|
| `<64-hex>.snapshot.json` | 以 snapshot identity 命名的 immutable reproducibility manifest。 |
| `<64-hex>.md` / `<64-hex>.json` | 以內容 SHA-256 命名的 supporting evidence。 |
| `<timestamp>_<mode>_<run-id>.json` | 一次 online/offline formal execution 的完整 result payload。 |
| `latest.json` | 已退役 legacy experiment 的最後 retained result；不是 current authority。 |
| `prev_N.json` | Legacy experiment 的 retained predecessor。 |
| `*.migration-parity.json` | Migration 前後的 parity evidence。 |
| `*.migration-result.json` | 引用 parity evidence 的 migration envelope。 |
| `development-gate.json` | Study Development gate evidence。 |
| `development-selection.json` | Guarded candidate/family selection evidence。 |

## 常用唯讀查找

列出所有 Study 結論：

```bash
find workflows -path '*/work/studies/*/CONCLUSION.md' -print | sort
```

查看 snapshot 的核心 identity，不展開整份 JSON：

```bash
jq '{snapshot_id, decision_time, data, definition}' \
  results/research-trials/<family>/<trial>/<snapshot-id>.snapshot.json
```

查看 legacy result 的頂層結構與 validity：

```bash
jq 'keys' legacy/results/<experiment>/latest.json
uv run trading result status <experiment>
```

查某個舊路徑搬到哪裡：

```bash
jq --arg path 'results/<old-path>' \
  '.migrations[] | select(.old_path == $path)' \
  results/registries/path-migrations.json
```

驗證全部 tracked workflow metadata 與 immutable evidence：

```bash
uv run trading workflow validate --all
```

## 修改與清理原則

- 不手動編輯 generated JSON、content-addressed evidence、registry 或 frozen Study artifact。
- 不以「檔名看不懂」、「檔案很大」或「似乎重複」作為刪除依據；先追查引用與 authority。
- 不直接修正 frozen artifact 內的舊路徑；由 `path-migrations.json` 保留可驗證的歷史關係。
- 新 artifact 應由對應 CLI/workflow command 產生，並遵循 `.gitignore` 的 retained policy。
- `results/` 不放 broker exports、credentials、個人交易狀態或 provider cache；這些都屬 local-only
  boundary，且不可 commit。
