# Trading Workflow Authoring Simplification Implementation Plan

**Goal:** 簡化 `trading-author-workflow` 新增、修改與停止使用 repository workflow 的流程，
同時保留 released workflow immutability、human authority、study safety、release evidence 與既有
workflow/change history 的完整相容性。

**Architecture:** 先將 skill 改為 progressive disclosure，但保留舊 authoring-contract 路徑作
相容入口，並同步更新 study operation/evaluation callers。接著建立 crash-safe authoring
transaction substrate，再讓 repository 同時讀取 legacy 五檔 change records 與新的單一
author-edited `CHANGE.md`。所有既有與新增 authoring mutation、所有會寫入 `workflows/` 的 study
mutation，以及 non-dry-run qualification study registration，都共用 repository lock；authoring
mutations 再透過 durable journal、shadow validation 與 deterministic recovery 發布。
最後加入 create/change/evolve happy paths，自動配置 identity、更新 registry、同步 index 並驗證。
停止使用 workflow 時依 lifecycle 映射成 abandon 或 terminal retire；任何
registered/released history 都不做實體刪除。

**Affected domain:** 本計劃只改 workflow authoring tooling、相關 author/operate/evaluate skill
instructions、templates、CLI、tests、local authoring transaction state 與相關文件。它不修改任何
released `WORKFLOW.md`、既有 study、research definition、研究 outcome、qualification evidence
或 trading authority。

## Desired user experience

### 新增 workflow family

```text
理解來源與需求
→ 顯示完整 draft 與尚未決定事項
→ 人類確認 identity／authority／research-validity 決策
→ 原子建立 v001 draft、registry entry 與 indexes
→ validate
→ 另行取得 release approval
```

使用者或 Agent 不再手動配置 `v001`、複製 template、替換 `REPLACE_ME`、編輯 root registry、
執行 sync，或在失敗時清理半完成的 authoring state。

### 修改 active workflow

```text
分析 active workflow 與 study impact
→ 顯示 change preview
→ 建立單一 proposed CHANGE.md
→ 人類接受／拒絕／延後
→ 從 accepted changes 原子建立唯一 next-version draft
→ validate
→ 另行取得 release approval
```

### 停止使用 workflow

```text
unregistered local draft → 只有 never-tracked/unreferenced 才能 exact-path deletion，需明確確認
registered draft          → abandon
active workflow           → terminal retire，需 human approval、safe-study check 與 close dispositions
released terminal history → 永久保留，不實體刪除
```

## Global constraints

- 不修改或搬移任何既有 released workflow、release evidence、change record 或 study bytes。
- Legacy 五檔 change format 永久保持讀取與驗證相容；新 authoring 一律寫 schema v2。
- 一個 workflow family 最多一個 `active` 與一個 `draft` version。
- Released `WORKFLOW.md`、normative dependency digests 與 pinned references 維持 immutable。
- Human approval 仍是 change decision、retirement 與 release preparation 的必要條件。
- Active version 被 supersede 或 retire 前，unfinished studies 必須為 `paused`、`completed` 或
  `cancelled`。Replacement release 依既有規則處理 continue/restart/close dispositions；純
  retirement 只能將 paused studies 標為 `close-invalidated`。
- 新增與修改操作不得接受 caller 指定 allocated `Cxxx`、`vNNN` 或 current-time evidence。
- 每個 authoring mutation（包括既有 change/version transition、release、standalone sync，以及
  新 create/evolve）、每個 `WorkflowStudyService` write，以及 non-dry-run
  `qualification plan register-study` 都必須使用同一 repository-scoped lock。所有 writer 取得
  lock 後必須先處理 pending authoring journal，再重讀 lifecycle preconditions；任何
  outcome-relevant writer 都不得繞過 crash recovery gate。Authoring mutation 另使用 durable
  transaction protocol。捕捉到的 exception、process crash、host/power loss 或重新啟動後，不得
  留下不可判讀的 partial state。既有 study lifecycle states 與 outcome authority 不因此改變。
- `workflows/README.md` frontmatter 繼續作 lifecycle authority，不搬移 registry storage。Task 8
  在同一 PR 將 repository 的 root registry 由 schema 1 升為 schema 2；這是唯一 metadata schema
  migration，不重寫任何 version、release、change 或 study bytes。
- 不新增可任意刪除 registered workflow history 的 CLI。
- 不編輯 `pm/`。
- 新增 public CLI、重複檔案 pattern、generated retirement evidence 或 local-only transaction
  state boundary 時，同一 task 更新
  `docs/ARCHITECTURE.md`。
- 實作 executable behavior 時先寫 focused failing tests，再完成最小實作。

## Compatibility decisions

以下決策在實作開始前視為本計劃的固定預設；若要改變，應先更新本計劃或另立設計決策：

1. **Legacy read compatibility is permanent.** 既有
   `README.md + PROPOSAL.md + IMPACT.md + VALIDATION.md + DECISION.md` 不遷移、不重寫。
2. **New writes use schema v2 only.** 新 change directory 以 `CHANGE.md` 作唯一 author-edited
   authority；human decision 後只允許 writer 另建 add-only generated decision-event sidecars。
3. **No mixed representation.** 同一 change directory 同時出現 legacy 與 v2 authority 時，
   validation fail closed。
4. **Source-change paths remain directory paths.** Version metadata 與 release evidence 的
   `source_changes` 繼續指向 change directory，不因內部格式改變而破壞 lineage；schema-v2
   release 另保存每個 terminal `CHANGE.md` 與 decision-event manifest 的 digest，形成 directory
   path 外部的 immutable anchor。
5. **Registered history is never physically deleted.** `abandoned`、`superseded`、`retired` 與
   released entries 永久留在 registry。
6. **Old CLI command names remain available, not unsafe argument forms.** 新 happy-path commands
   先作 additive interface；既有 `change transition`、`version transition`、`sync` 與 `release`
   不立即移除。但 `version transition --to retired` 必須新增與 `retire` alias 相同的 reason、
   disposition 與 evidence guard，舊的無 evidence invocation fail closed。
7. **Crash-safe recovery is required.** Authoring atomicity 不只涵蓋 Python exception rollback，
   也涵蓋 commit decision 前後的 process crash。Journal 位於 local-only
   `state/workflow-authoring/`；tracked repository 只保存 transaction 完成後的 canonical bytes。
8. **Existing replacement drafts are updated in place.** 同一 family 已有 registered draft 時，
   `evolve` 更新該 draft 的完整 contract、metadata 與 accepted `source_changes`，不 abandon、
   不配置新版本號。
9. **Semantic completeness remains human-reviewed.** CLI 只驗證可機械判斷的結構、identity、
   schema、path、placeholder 與 lifecycle；11 項 workflow semantic coverage 仍由 Agent preview
   與 human confirmation 判斷。
10. **Never-used allocation includes history and concurrency.** Allocator 在同一 repository lock
    內掃描 registry、現存 paths、current inbound references、Git path history，以及 Git 歷史內容
    中的 exact repository-relative identity references。曾 tracked 或 referenced 的 identity 永不因
    目錄刪除而重用。
11. **Initial identity is always v001.** 新 family 只能建立 `v001`。若同 slug 的 `v001` 曾出現在
    registry、filesystem、Git path/history content 或 inbound reference，CLI 視為 collision／
    governance repair，而不是建立 initial `v002`。
12. **Retirement is terminal in this plan.** 純 retirement 不建立 replacement version，也不接受
    continue/restart dispositions。未來若要復活 retired family，必須另立 lifecycle 設計。
13. **Dispositions are machine-enforced authorization.** Replacement/retirement dispositions 不只是
    文件敘述；study initialization 與 repository validation 必須執行 exact mapping、single-use 與
    close-invalidated 規則。
14. **Unknown capabilities fail closed for new authoring.** 新 draft/release 的 capability 必須存在於
    single canonical supported registry；legacy bytes 維持讀取相容。Release 另驗證恰有 market、
    broker、execution 與 portfolio-risk 四種 resolved policy kinds。
15. **Never-used proof requires complete local Git history.** Allocation 在 non-Git、shallow clone、
    Git timeout/non-zero 或無法掃描所有 locally reachable refs 時 fail closed；不得把不確定性當成
    identity 可用。
16. **Release readers are dual-schema before v2 writes.** Task 7 在任何 schema-v2 release 可成為
    active 前，先讓 authoring、workflow-native execution、research CLI 與 qualification readers
    共用 closed-schema v1/v2 parser；schema v1 沒有 dispositions 只代表不能授權新的跨版本 revisit。
17. **Revisit actions have machine meaning.** Same-version source 必須是 `draft`、`cancelled` 或
    `completed`；其他 open states fail closed。Cross-version `continue` 只可源自 `paused` study，
    並要求新 study preregistration 時的 hypothesis bytes 與 source frozen hypothesis 完全一致；
    `restart` 亦只可源自 `paused`，但允許新 hypothesis/plan。兩者都建立新的 preregistration、
    evidence 與 outcome identity；`close-invalidated` 不可消耗。
18. **Authoring basis is audit provenance.** Draft 可在受控 update 中替換 authoring basis；release
    schema v2 必須複製 normalized basis 並 pin canonical JSON digest，之後不得漂移。

## Task 1: Establish authoring compatibility baselines

**Files:**

- Modify: `tests/test_workflow_authoring.py`
- Read/verify: `workflows/README.md`
- Read/verify: `workflows/strategy-forward-replication-research--v001/` through `--v008/`
- Read/verify: `.agents/skills/trading-author-workflow/`

**Interfaces:**

- Current `WorkflowRepository.validate_all()` behavior.
- Current change/version/release transitions.
- Existing workflow registry, legacy change directories, and generated indexes.

- [ ] Add a fixture that mirrors a complete legacy five-file change record and prove it can move
  through `draft -> proposed -> accepted -> released` without byte migration.
- [ ] Add a repository-level regression asserting the existing tracked v001–v008 registry and
  released artifacts validate unchanged.
- [ ] Add a test that records the current release invariants: human approval, exact source changes,
  safe unfinished-study boundary, dependency digests, policy pins, and no backdated clock.
- [ ] Characterize current mutation ordering，但不要求 post-write rollback：證明 precondition failure
  不改變 state，並以 injected post-write/sync failure 測試記錄現況可能留下 partial state。這些
  characterization tests 在 Task 3 transaction substrate 完成後才改成 recovery assertions。
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring.py
uv run trading workflow validate --all
```

Expected: current behavior 與現存 atomicity gap 都被固定記錄；Task 1 不假裝只靠 tests 就能讓
現行 release/transitions 達成 crash-safe 保證。

## Task 2: Refactor `trading-author-workflow` for progressive disclosure

**Files:**

- Modify: `.agents/skills/trading-author-workflow/SKILL.md`
- Modify: `.agents/skills/trading-author-workflow/references/workflow-authoring-contract.md`
- Create: `.agents/skills/trading-author-workflow/references/core.md`
- Create: `.agents/skills/trading-author-workflow/references/create.md`
- Create: `.agents/skills/trading-author-workflow/references/evolve.md`
- Create: `.agents/skills/trading-author-workflow/references/remove.md`
- Create: `.agents/skills/trading-author-workflow/references/release.md`
- Create: `.agents/skills/trading-author-workflow/references/impact.md`
- Create: `.agents/rules/workflow-study-governance.md`
- Create: `.agents/rules/workflow-version-boundary.md`
- Modify: `.agents/skills/trading-operate-workflow/SKILL.md`
- Modify: `.agents/skills/trading-evaluate-study/SKILL.md`
- Modify: `.agents/skills/trading-author-workflow/agents/openai.yaml`
- Modify: `docs/ARCHITECTURE.md`

**Skill routing contract:**

- `SKILL.md` contains only trigger boundaries, mode selection, shared precedence, mutation authority,
  progressive-disclosure routing, and the finish report.
- Every mode reads `core.md` plus only its relevant mode reference.
- `review` 先讀 `core.md`，再依受審 object 動態載入必要 mode contract：initial draft/import 讀
  `create.md`、change/replacement 讀 `evolve.md`、abandon/retirement 讀 `remove.md`、release
  readiness 讀 `release.md`；只要涉及 active-version 或 unfinished-study impact 就再讀
  `impact.md`。Review 不因唯讀而省略受審行為的治理規則，也不載入無關 mode。
- `document-led creation`, `guided creation`, and import read `create.md`.
- `evolution` reads `evolve.md`; it reads `impact.md` only when an active version or unfinished study
  may be affected.
- `remove` reads `remove.md`; it reads `impact.md` only for an active version.
- `release preparation` reads `release.md` and `impact.md`.
- `trading-operate-workflow` 與 `trading-evaluate-study` 改讀 shared canonical
  `.agents/rules/workflow-study-governance.md`，不再要求
  載入 authoring create/evolve/remove/release 規則。
- Exact version-boundary safety、same/cross-version revisit、disposition、consumption 與 retirement
  closure 只存在於 `.agents/rules/workflow-version-boundary.md`。`impact.md`、shared study governance
  與 operate skill只在相關情境路由到它，不複製 normative rules；ordinary study operation/review
  不載入它。
- 原 `workflow-authoring-contract.md` 暫時保留為短 compatibility pointer，列出新 canonical
  references 並明確要求 caller 改用對應 mode；它不複製 normative content。
- Complete sources may be converted into one draft preview plus an unresolved-decision list.
- Identity, deletion, retirement, release, authority, and research-validity decisions remain
  individually confirmed; low-risk editorial decisions may be confirmed together.

- [ ] 先做 rule inventory：對每條現有說明標示 `keep`、`remove-generic`、`remove-duplicated`、
  `enforced-by-code` 或 `move-to-reference`。只保留會改變 Agent 決策的非顯而易見 invariants；
  不把整份舊 contract 機械拆成六份。
- [ ] 每條保留規則只存在於一個 canonical reference；`SKILL.md` 與 compatibility pointer 不
  重複 normative text。
- [ ] Routing tests允許 author impact與 study revisit情境共同載入 version-boundary reference，
  同時斷言它們不載入彼此無關的 authoring mode files。
- [ ] Preserve repository precedence, immutable released workflow behavior, source disposition,
  study scope separation, and release authority.
- [ ] Update skill frontmatter `description` so review、create、evolve、abandon、retire 與 release
  都可被正確選擇；同步更新 default prompt，但不把 UI prompt 當成 discovery authority。
- [ ] Update both maintained study skills to the new study-governance reference, then use `rg` to
  verify no maintained caller still requires the monolithic contract contents.
- [ ] Run the skill validator:

```bash
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-author-workflow
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-operate-workflow
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-evaluate-study
rg -n 'workflow-authoring-contract\.md' .agents/skills
```

- [ ] Exercise these read-only routing scenarios:
  - review an active workflow;
  - create from a complete Markdown source;
  - guided creation with missing authority decisions;
  - evolve an active workflow with one running study;
  - abandon a draft;
  - retire an active workflow;
  - prepare, but do not infer, a release.
- [ ] 為每個 routing scenario 斷言 required references 已載入、forbidden unrelated references 未
  載入；review change impact、retirement 與 release readiness 必須覆蓋各自 mode contract。
- [ ] 由一個沒有本計劃結論的 fresh independent agent，在隔離 temporary workspace 執行 realistic
  author／operate／evaluate routing forward-tests；不得修改真實 workflow 或 study。

Expected: ordinary authoring 只載入相關 mode，study operation/evaluation 仍能取得完整 lifecycle
規則，且 compatibility pointer 不成為第二份 authority。

## Task 3: Build the crash-safe authoring transaction substrate

**Files:**

- Create: `src/trading/core/workflow_authoring_transaction.py`
- Create: `src/trading/core/workflow_identity.py`
- Create: `tests/test_workflow_authoring_transaction.py`
- Create: `tests/test_workflow_identity.py`
- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/core/workflow_studies.py`
- Modify: `src/trading/core/study_qualification.py`
- Modify: `tests/test_workflow_authoring.py`
- Create: `tests/test_workflow_studies.py`
- Modify: `tests/test_study_qualification.py`
- Modify: `tests/test_qualification_workflow.py`
- Modify: `src/trading/cli.py`
- Modify: `.github/workflows/lint.yml`
- Modify: `CLAUDE.md`
- Modify: `.gitignore` only if the existing `state/` rule does not already cover the journal
- Modify: `docs/ARCHITECTURE.md`

**Lock and durability contract:**

- One repository-scoped filesystem lock serializes identity allocation、every authoring write、every
  `WorkflowStudyService` mutation that writes under `workflows/`, and non-dry-run study qualification
  registration. The lock implementation supports an explicitly passed/re-entrant lease so a study
  mutation can call index sync or qualification code can take its inner lock without deadlocking or
  releasing the boundary midway.
- Every scoped writer uses one `enter_workflow_mutation()` invariant: acquire the shared lock;
  inspect the pending authoring journal; automatically execute the deterministic action already
  selected by a valid `prepared`/`commit-decided` phase; fail closed with the status/recover command
  for corrupt/foreign/conflicting journals; then re-read registry, exact version, study inventory,
  and caller-specific lifecycle preconditions. Release/retire cannot rely on a safe-study check made
  before the lock; study init/resume cannot rely on an active-version check made before the lock.
- Global lock ordering is `workflow repository lock -> qualification lock`. Study completion paths
  that also need qualification state and non-dry-run `compile_study_qualification_plan()` must be
  refactored to acquire them in this order; no code path may acquire the qualification lock and then
  wait for the workflow lock. Dry-run qualification compilation remains read-only and acquires
  neither writer lock.
- Inside both locks, qualification registration re-reads the exact workflow registry、release、study
  README、frozen spec and completion state. It only registers a `running` study under the unique
  active version; a cross-version-created study must also have a valid release authorization、
  consumption artifact and pinned consumption digest. Superseded/retired versions、paused or
  terminal studies and missing/mismatched consumption fail before qualification registry mutation.
- A transaction computes the complete post-state in memory, including registry bytes, generated
  root/version indexes, lifecycle metadata, release/change artifacts, directory creates, and any
  allowed deletions. Each target records its repository-relative path, before/after kind
  (`absent`, regular file, or directory), POSIX mode where relevant, exact SHA-256, recoverable
  before bytes, and staged after location. Symlink targets fail closed.
- The plan also records a disjoint, assert-only validation read-set for every non-target byte whose
  value affects the computed after-state or guarded precondition: workflow definition、normative/
  pinned dependencies、policy registry/config/RELEASE evidence、study metadata and external immutable
  evidence. Each entry records path kind、mode and SHA-256. Source-change/registry/index metadata
  modified by release is protected by its complete target before-state instead of appearing twice.
  A path modified by the transaction must be a target, never both target and read assertion; metadata
  being rewritten by the operation cannot also serve as its own normative dependency.
- The first implementation supports only the operations this plan needs: regular-file replace,
  add-only regular file, and creation of a previously absent directory tree from an exact leaf-file
  manifest. It does not replace/delete arbitrary non-empty directories, follow symlinks, or expose a
  generic tree transaction API. Manual never-tracked local-draft deletion remains outside it.
- The crash model includes caught exceptions, process kill, and host/power loss under normal local
  filesystem fsync/atomic-rename guarantees. The protocol ordering is fixed:
  1. acquire the shared lock and recover or reject any prior operation;
  2. re-read all preconditions and snapshot target kinds, modes, bytes, and digests;
  3. compute the complete after-state, stage every after file/tree, fsync staged files, then fsync
     their staging directories;
  4. run overlay/shadow validation before modifying canonical targets. Filesystem reads use the
     overlay; Git-index evidence checks are injected against the real repository/index and map
     canonical paths explicitly instead of treating a plain shadow copy as another Git worktree;
  5. durably write and fsync the `prepared` journal plus its parent directory;
  6. compare-and-swap recheck every target's before-state and every assert-only read-set entry.
     Any mismatch leaves canonical bytes untouched, retains `prepared`, and reports the conflicting
     target/input path;
  7. durably replace the phase with `commit-decided` and fsync the journal parent;
  8. before publishing each still-unpublished target, confirm it still matches before-state; already
     published targets must match after-state. A third state fails closed instead of overwriting an
     editor/Git/uncoordinated writer change;
  9. publish each target idempotently, fsync every written file and affected parent directory, then
     verify exact after kinds/modes/digests;
  10. verify transaction-owned target invariants and exact after-state, durably mark `complete`,
      then remove journal/staging bytes and fsync their parents. A crash may therefore leave a
      `complete` journal with absent or partially removed staging, but canonical publication is done;
  11. run full canonical repository validation as post-commit health reporting. Non-target drift
      occurring after commit decision may make the repository invalid and must be reported, but it
      does not reopen/retain an otherwise fully published journal or repeatedly roll forward stale
      bytes.
- A local-only journal under `state/workflow-authoring/` stores schema version, repository identity,
  operation ID/type, complete target manifest, assert-only validation read-set, before/after values,
  staged paths, and phase.
  `prepared` recovery never writes canonical targets: because publication has not begun, it may
  discard staging/journal only when every target still matches recorded before-state; any other state
  fails closed instead of overwriting an external update. `commit-decided` recovery rolls forward
  the exact after-state and cannot be aborted. `complete` recovery requires every target to match
  after-state, then performs cleanup only; missing staging is already-clean and does not fail.
  Any phase/target combination outside these rules fails closed with the exact conflicting path.
- Orphan staging created before a durable `prepared` journal may be removed only after proving no
  journal references it. A corrupt, foreign-repository, or incompatible journal blocks every new
  mutation; callers cannot replace its operation or inputs.
- Standalone `workflow sync`, existing change/version transitions, and `release` use the same
  transaction coordinator. Read-only validation and status never create or recover a transaction
  implicitly. An explicit recovery command exists for diagnosis and blocked startup.

**Repository interfaces:**

- `WorkflowAuthoringTransaction.prepare(...)`
- `WorkflowAuthoringTransaction.commit()`
- `WorkflowAuthoringTransaction.recover()`
- `WorkflowRepository.recover_pending_authoring_transaction()`
- `WorkflowRepository.abort_prepared_authoring_transaction(...)`
- `WorkflowRepository.authoring_transaction_status()`
- Shared `WorkflowRepositoryMutationLock` lease used by `WorkflowRepository` and
  `WorkflowStudyService`, and passed into non-dry-run study qualification registration.

**Operational CLI:**

```bash
uv run trading workflow authoring status
uv run trading workflow authoring recover
uv run trading workflow authoring abort-prepared <operation-id> \
  --reason <reason> --by <stable-operator-id>
```

`status` is read-only. `recover` requires the shared lock and only applies the phase already durably
recorded; it never accepts replacement operation inputs or a caller-selected rollback direction.
Normal authoring and study writers automatically recover a valid journal through the same mutation
entry invariant; explicit `recover` exists for diagnosis/retry after an operator has resolved a
reported conflicting target. `abort-prepared` is the only discard path: it requires the exact
operation ID、stable actor and reason, is legal only while phase is `prepared`, never changes
canonical targets, appends a local-only audit record, then removes journal/staging durably. It is
used only after the operator accepts abandoning an operation whose targets/read-set conflicted.
`commit-decided` cannot be aborted; corrupt or conflicting journals are never auto-rewritten.

**Identity proof contract:**

- `workflow_identity.py` provides one fail-closed reservation scanner for `vNNN`、`Cxxx`, and
  `Sxxx`. It searches current registry/filesystem、stage-0 Git index plus every locally reachable
  commit/ref with
  kind-specific grammar and token boundaries:
  - version: exact `workflows/<slug>--vNNN` path or standalone canonical `<slug>@vNNN` token;
  - change: a `*--cNNN` basename counts only when its complete parent path parses under the exact
    source version; canonical `<slug>@vNNN/Cxxx` counts in any UTF-8 text blob; bare `Cxxx` counts
    only when the same Markdown/YAML/JSON document has unambiguous workflow+source-version metadata;
  - study: the equivalent complete parent-path rule, canonical `<slug>@vNNN/Sxxx`, or bare `Sxxx`
    only with unambiguous workflow+workflow-version metadata in the same document.
  Basenames are never reserved globally across unrelated versions, and narrative bare IDs without
  version scope do not reserve another family's local number.
- Non-Git worktrees, `git rev-parse --is-shallow-repository == true`, command timeout/non-zero,
  unreadable objects, or inability to enumerate `git rev-list --all` fail closed with an actionable
  “cannot prove never-used” error. No exception/timeout is converted to an empty history result.
- The guarantee covers complete locally reachable `--all` history; canonical CI performs the same
  check in a non-shallow clone. Allocation does not claim knowledge of commits never fetched into
  any local ref.
- Historical path and textual-content proofs are separate. Complete path history comes from one
  NUL-delimited `git log --all --name-status --format=` traversal; parser handles both old/new names
  for rename/copy records and every added、modified、deleted path. Historical textual content uses
  `git rev-list --objects --all` only to enumerate object IDs, confirms object type, de-duplicates
  blob OIDs, and reads bytes through `git cat-file --batch`; the optional path printed beside a blob
  OID is never treated as a complete path inventory.
- Current proof enumerates tracked paths with `git ls-files -z`, stage-0 index paths/OIDs/modes with
  `git ls-files --stage -z`, and untracked non-ignored paths with
  `git ls-files --others --exclude-standard -z`. Any unmerged index stage、symlink encountered where
  regular-file content is required、command error or undecodable claimed text fails closed. Path
  grammar scans every enumerated path; textual grammar scans every regular UTF-8 file/blob and skips
  only bytes classified as binary by a documented NUL/type rule. Ignored files、`.git/` and local
  `state/` are outside the reservation universe.
- A local-only cache under `state/workflow-authoring/identity-scan-v1.json` separately stores the
  complete historical-path result and de-duplicated textual-blob result, keyed by repository
  identity、scanner schema and SHA-256 of sorted ref-name/OID pairs. Current worktree、stage-0 index、
  untracked-nonignored paths and registry always rescan. The default historical scan budget is 120
  seconds; timeout errors report stage、path/object count and cache/ref fingerprint, fail closed, and
  never publish a partial reservation result.
- The reservation proof returns virtual CAS assertions for sorted ref tips、the complete stage-0
  index tuple set and relevant current directory/path inventory. Immediately before commit decision,
  allocation reruns the proof against the planned overlay and requires the same proof token except
  for declared transaction targets; ref、index or inventory drift aborts without publication.

- [ ] Write failing tests for exclusive/re-entrant lease behavior, exact path kind/mode/absence and
  before/after plans, staged shadow validation with real-index mapping, rollback before commit
  decision, roll-forward after commit decision, corrupt journal, wrong repository identity,
  changed staged bytes, a canonical target matching neither digest, orphan staging, idempotent
  recovery, and incompatible retry. Add crash-after-complete、journal-unlink、staging-unlink and
  parent-fsync boundaries; prove prepared recovery never writes canonical bytes and complete recovery
  performs cleanup only.
- [ ] Add read-set tests covering dependency、policy release、study-precondition and evidence drift,
  plus target-before-state tests for source changes, before commit decision; each must abort without
  canonical mutation. Drift after
  commit decision must not prevent a fully published journal from completing, but full validation
  must report the repository health failure.
- [ ] Reject undeclared normative reads in operation planners and target/read-set overlap. Add a
  release fixture proving generated registry/index/change targets cannot be selected as their own
  normative dependency.
- [ ] Add CAS tests where an editor/uncoordinated process changes a target during shadow validation,
  immediately before commit decision, and between publications. Prove pre-decision mismatch causes
  no canonical mutation and post-decision third-state conflict fails closed without overwriting it.
- [ ] Inject failure before and after every publication boundary for `sync`, `transition_change`,
  `transition_version`, and `release`, including process-kill tests at every phase switch; start a
  fresh repository process and prove deterministic recovery reaches exactly the before- or
  after-state selected by the journal phase. Verify file and parent-directory fsync ordering with
  a recording filesystem adapter rather than relying only on happy-path integration tests.
- [ ] In Task 3, test concurrent reservation primitives and existing study allocation without
  depending on not-yet-added create/evolve commands. Tasks 5–6 add end-to-end concurrent
  create/change/evolve tests using the same scanner and lock.
- [ ] Route study init、preregister、transition、freeze、complete 與 any other study writer through
  the common mutation-entry gate, auto-recovering valid pending journals before re-reading
  active/version/study preconditions inside the lease. Enforce workflow-lock-before-qualification-
  lock ordering. Add
  authoring-vs-study race tests proving release/retire cannot be crossed by concurrent study init or
  paused-to-running resume, and concurrent study sync cannot overwrite a transaction's planned
  index bytes.
- [ ] Route non-dry-run `compile_study_qualification_plan()` through the same mutation entry, then
  acquire its existing qualification lock. Add races against release、retire and study completion;
  add pending prepared/commit-decided/complete journal tests and prove registration only proceeds
  after in-lock active/running/consumption validation.
- [ ] After a crash at every prepared/commit-decided/publication phase, immediately invoke each
  study writer and prove it first completes the selected authoring recovery or fails without writing.
- [ ] Add reservation tests for all canonical path/text spellings, version-scoped local IDs,
  non-Git/shallow repositories, Git timeout/non-zero, missing objects, and `Sxxx` historical/inbound
  references; preserve permanent local scoping between unrelated workflow versions. Include the
  same blob OID at multiple historical paths、rename/delete history、stage-0-only reference、unmerged
  index、untracked-nonignored reference、ignored-file exclusion and ref/index/inventory CAS drift.
  Add cache hit/invalidation、blob de-duplication、token-boundary and deterministic timeout diagnostics.
- [ ] Add parser/dispatch tests for `workflow authoring status/recover/abort-prepared`, including clean
  state, prepared cleanup without canonical rollback, explicit audited prepared abort,
  commit-decided roll-forward, complete cleanup, corrupt journal refusal, and read-only status.
- [ ] Update `.github/workflows/lint.yml` to checkout with `fetch-depth: 0`, assert
  `git rev-parse --is-shallow-repository` is `false`, and run workflow authoring transaction、identity、
  study lifecycle、study qualification and qualification workflow suites in addition to existing
  authoring/policy validation. CI must exercise the same fail-closed history proof as local tests.
- [ ] Retrofit existing authoring mutations before adding new schema-v2 writers or happy-path CLI.
- [ ] Replace Task 1 characterization expectations with crash-safe assertions once the coordinator
  is active.
- [ ] Keep the journal local-only and free of credentials, broker exports, private ledgers, market
  outcomes, or other trading data.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring_transaction.py tests/test_workflow_identity.py \
  tests/test_workflow_authoring.py tests/test_workflow_studies.py tests/test_study_qualification.py \
  tests/test_qualification_workflow.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: every existing authoring mutation is serialized and recoverable across exceptions、
process restarts and the documented filesystem crash model; study writers and non-dry-run
qualification registration share the same safe version boundary before new create/evolve behavior
is introduced.

## Task 4: Add schema-v2 single-authority change records

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Retain temporarily: `.agents/skills/trading-author-workflow/assets/change/` legacy five-file assets
- Create: `.agents/skills/trading-author-workflow/assets/change-v2/CHANGE.md`
- Generated pattern: `<change-path>/decision-events/DNNN-<event-sha256>.json`
- Modify: `.agents/skills/trading-author-workflow/references/evolve.md`
- Modify: `.agents/skills/trading-author-workflow/references/impact.md`
- Modify: `CLAUDE.md`
- Modify: `docs/ARCHITECTURE.md`

**Schema-v2 contract:**

```markdown
---
schema_version: 2
id: C001
title: Example change
workflow: example-workflow
source_version: v001
status: proposed
created_at: "2026-08-18"
status_changed_at: "2026-08-18T00:00:00.000000Z"
decided_at: null
decided_by: null
decision_history: []
released_in: null
---
# Example change

## Proposal

...

## Impact

...

## Validation

## Decision
```

**Internal model:**

- Introduce one normalized internal change representation, independent of disk format.
- Legacy reader maps the five files into the normalized proposal, impact, validation, and decision
  fields.
- Schema-v2 reader maps `CHANGE.md` sections into the same fields.
- Transition, validation, release, index rendering, and blocking-change checks consume only the
  normalized representation.
- The normalized model exposes a presentation target: legacy index links resolve to the existing
  directory/README, while schema-v2 links point directly to `CHANGE.md`.

**Section completeness by state:**

- Every schema-v2 `CHANGE.md` has exactly four level-2 authority sections named `Proposal`, `Impact`,
  `Validation`, and `Decision` in that order. It may have one title H1 and writer-generated
  `### DNNN — <status>` snapshots under Decision. Caller-authored inputs may not add another H2 or
  use the reserved DNNN H3 grammar.
- `draft`: sections may be empty, but scaffold tokens (`REPLACE_ME`, `[TODO`, `TODO:`) are invalid.
- `proposed`: `Proposal` and `Impact` must be substantive; `Validation` may be empty. `Decision` is
  empty on first proposal but remains substantive when a deferred decision snapshot already exists.
- `accepted`, `rejected`, or `deferred`: all four sections must be substantive and the decision
  metadata must contain current-time human approval.
- `withdrawn`: `Decision` must be substantive; other section requirements retain the current
  contract's weaker pre-decision semantics.
- `released`: all four sections remain substantive, decision metadata is immutable, and release may
  set only `released_in` plus the released lifecycle fields.

**Closed frontmatter and lifecycle matrix:**

- Schema v2 accepts exactly these top-level keys: `schema_version`, `id`, `title`, `workflow`,
  `source_version`, `status`, `created_at`, `status_changed_at`, `decided_at`, `decided_by`,
  `decision_history`, and `released_in`. Unknown or missing keys fail closed.
- `schema_version` is integer `2`; ID、workflow slug、source version and path must agree with
  `Cxxx`/lowercase-kebab-case/`vNNN` identities; title is non-empty; status is a known lifecycle
  value. Writer-generated dates/timestamps use the repository's canonical UTC formats and are not
  caller-backdateable. `released_in` is null or the exact registered replacement `vNNN` selected by
  release.
- `draft`: `status_changed_at`、`decided_at`、`decided_by`、`released_in` are null and
  `decision_history` is empty.
- First `proposed`: `status_changed_at` is service-generated current time; current decision fields
  and `released_in` are null; history is empty. A `deferred -> proposed` transition preserves
  `decision_history`, clears current `decided_at/decided_by`, and generates a new
  `status_changed_at` without erasing prior section content.
- `accepted`、`rejected`、`deferred`: `status_changed_at == decided_at`, `decided_by` is a stable
  human identity, `released_in` is null, and the last history item exactly matches the current
  decision.
- Each `decision_history` item has exactly `sequence`, `status`, `recorded_at`, `recorded_by`,
  `validation_sha256`, `decision_sha256`, `snapshot_sha256`, `event_path`, and `event_sha256`.
  Status is `accepted`、`rejected`、`deferred`, or `withdrawn`; withdrawal has null
  `validation_sha256`, while all other digests are exact 64-hex values. Sequence begins at 1 without
  gaps, timestamps are canonical current-time UTC and strictly increase, and frontmatter items must
  exactly match both the generated Decision snapshot and its decision-event sidecar.
- Legal history is zero or more `deferred` items followed by at most one terminal
  `accepted`、`rejected`, or `withdrawn` item. Deferred reproposal does not append an event. Released
  changes require the unique terminal item to be `accepted`; terminal items can never be followed by
  another event.
- The top-level Validation section contains the latest working validation body. The Decision section
  is an append-only sequence of writer-generated `### DNNN — <status>` snapshots. Each snapshot
  embeds the exact Validation and Decision input bytes used for that event, stable actor/time fields,
  and delimiters; `snapshot_sha256` covers the canonical serialized snapshot. A later proposal or
  decision may replace the working Validation section but never edits/removes prior Decision
  snapshots, so every historical rationale is replayable without relying on Git commit timing.
- Each human decision/withdrawal transaction also creates one add-only canonical-JSON event at
  `decision-events/DNNN-<event-sha256>.json`. The event contains exactly `schema_version`、canonical
  change identity/path、sequence、status、recorded_at、recorded_by、the exact Validation/Decision input
  bytes or null where withdrawal permits it, their digests, and `snapshot_sha256`; `event_sha256`
  hashes the complete canonical event bytes and determines the filename. The event is a generated
  immutable anchor, not a second authoring surface. CHANGE history and rendered snapshot must match
  it byte-for-byte.
- Validator rejects modification/removal of any current event, a filename/content digest mismatch,
  duplicate sequence, or disappearance of an event path that appears in the stage-0 index or locally
  reachable Git path history. Thus rewriting `CHANGE.md` and recomputing every digest still fails
  against the add-only event. Non-Git、shallow、unmerged-index or incomplete-history proof fails closed
  for schema-v2 decision mutation/validation.
- `withdrawn`: `status_changed_at` is current time, current `decided_at/decided_by` and
  `released_in` are null, and the last history item is a withdrawal snapshot with actor and reason.
  Withdrawal does not masquerade as a human accept/reject/defer decision.
- `released`: the accepted `decided_at/decided_by` and complete history are unchanged,
  `released_in` equals the replacement version, and only release may generate the released
  `status_changed_at`.
- All timestamps and decision-history digests are writer-generated or independently recomputed;
  caller metadata cannot supply current-time evidence.

**Decision write path:**

```bash
uv run trading workflow change decide <change-path> \
  --to <accepted|rejected|deferred> \
  --validation <validation-body-md> \
  --decision <decision-body-md> \
  --approved-by <human-id>

uv run trading workflow change withdraw <change-path> \
  --decision <withdrawal-body-md> --by <identity>
```

`change decide` writes the latest Validation body, appends an exact Validation/Decision snapshot、
creates its add-only event and publishes lifecycle metadata/history in one authoring transaction.
`change withdraw` does the equivalent for its withdrawal snapshot/event; it records an actor but is
not human approval of a research decision. The legacy low-level `change transition` remains
available for pre-authored legacy-format content.

For schema v2, low-level transition handles only `draft -> proposed` and `deferred -> proposed`.
Accepted/rejected/deferred decisions must use `change decide`; withdrawal must use
`change withdraw`. Callers can never pre-author or override history metadata or generated snapshots.
This restriction applies only to schema-v2 writes and does not rewrite legacy records.

`--validation` and `--decision` are substantive UTF-8 Markdown body fragments, not complete
documents. They must be regular non-symlink files, contain no YAML frontmatter, reserved four-section
heading, generated snapshot delimiter, or scaffold token, and resolve without path/symlink escape.
The same input boundary applies to `change decide` and `change withdraw`.

- [ ] Write failing tests for a valid v2 change, exact allowed frontmatter keys/types, every required
  section, and the complete section/metadata state matrix above, including first proposal,
  multiple deferred reproposals, terminal decision uniqueness, withdrawal after deferral, strict
  timestamp/sequence ordering, exact snapshot/event replay, tampered snapshot/digest/event rejection,
  historically tracked event deletion/rename, and release. Include a test that tampers with
  `CHANGE.md` and recomputes every in-file digest but still fails against the event anchor.
- [ ] Write failing tests for mixed legacy/v2 representation, unknown schema version, identity/path
  mismatch, duplicate ID, placeholder content, missing decision approval, illegal lifecycle, and
  invalid `released_in`.
- [ ] Preserve all current legacy-format tests without rewriting their fixtures to v2.
- [ ] Update `transition_change()` so v2 metadata transitions atomically update `CHANGE.md` while
  legacy transitions continue updating legacy `README.md`.
- [ ] Add `change decide` parser/dispatch/service tests proving content and approval become visible
  together or recover together through the Task 3 transaction protocol. Cover symlink、frontmatter、
  scaffold、reserved-heading and non-UTF-8 decision-input rejection.
- [ ] Add explicit `change withdraw` parser/dispatch/service tests for allowed source states, actor,
  exact reason snapshot, input validation, transaction recovery, and refusal after a terminal event.
- [ ] Update release processing so a draft version may reference accepted source changes in either
  representation and marks them released in their native format.
- [ ] Update generated work indexes to render identical columns/status while linking each format to
  its normalized presentation target; add snapshot assertions for both links.
- [ ] Keep legacy assets until the schema-v2 writer and all maintained skill callers pass Task 9
  verification. New writes use only `assets/change-v2/CHANGE.md` and never copy unfinished tokens
  into a proposed change.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: old bytes remain authoritative and valid; new changes use one author-edited authority plus
writer-generated immutable decision events and have equivalent lifecycle、impact、decision、release
and stronger audit semantics.

## Task 5: Add atomic change creation and workflow draft creation

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Create: `src/trading/core/workflow_capabilities.py`
- Modify: `src/trading/core/workflow_studies.py`
- Modify: `src/trading/core/study_qualification.py`
- Modify: `src/trading/core/policy_authoring.py`
- Modify: `src/trading/policies/resolver.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `tests/test_workflow_studies.py`
- Modify: `tests/test_study_qualification.py`
- Modify: `tests/test_policy_authoring.py`
- Modify: `tests/policies/test_policy_resolver.py`
- Modify: `.agents/skills/trading-author-workflow/references/create.md`
- Modify: `.agents/skills/trading-author-workflow/references/evolve.md`
- Modify: `CLAUDE.md`
- Modify: `docs/ARCHITECTURE.md`

**Repository interfaces:**

- `WorkflowRepository.create_initial_draft(...) -> Path`
- `WorkflowRepository.create_change(...) -> Path`
- Shared staging/publish helper for directory plus registry/index mutation.

**CLI happy paths:**

```bash
uv run trading workflow create \
  --slug <slug> --title <title> \
  --definition <complete-workflow-md> \
  --metadata <draft-metadata.json> [--source <original-source>]

uv run trading workflow change create <active-version-path> \
  --slug <change-slug> --title <title> \
  --document <complete-change-body-md>
```

**Closed initial-draft metadata schema:**

```json
{
  "schema_version": 1,
  "derived_from": null,
  "capabilities": [],
  "policies": [],
  "dependencies": [],
  "authoring_basis": {
    "mode": "guided",
    "confirmed_decisions": []
  }
}
```

- Exactly these six top-level keys are required; unknown or missing keys fail closed.
- `derived_from` is either null or an object containing exactly `workflow`, `version`, and `path`;
  all three must resolve to the same registered existing version.
- `capabilities` is an ordered list of unique lowercase kebab-case strings found in the single
  canonical supported registry in `workflow_capabilities.py`. New authoring rejects unknown values;
  `WorkflowRepository`、`WorkflowStudyService`、study qualification and CLI all import the same
  registry and behavior lookup. No capability literal or second supported set remains in those
  consumers. Permanent legacy readers do not rewrite or retroactively reject already released/
  superseded/retired historical bytes solely for an unknown legacy capability, but every draft
  entering the new release path must use supported values.
- Every policy item contains exactly `family`, `version`, `path`, and `release_digest`; family values
  are unique lowercase kebab-case identities, version/path must agree with the policy registry, and
  duplicate policy families fail closed. `release_digest` is either the exact 64-hex digest of a
  released policy's `RELEASE.json`, or null only while both the selected policy and workflow version
  are drafts. Release preparation resolves/requires every digest and rejects null or stale values.
- Policy resolution also returns the authoritative policy `kind`. Release requires exactly one
  resolved `market`, `broker`, `execution`, and `portfolio-risk` kind, with no missing/duplicate/extra
  kind; draft null-digest selections must still resolve through the policy registry so their kind is
  known before release.
- `PolicyResolver.inspect_registered(family, version)` is the single read-only authority for draft
  and released selection metadata. It validates registry status/path and closed policy config keys
  `schema_version`、`family`、`version`、`kind`、`values`, confirms identity/path agreement, and returns
  exact status/kind without treating a draft as executable. Existing `resolve()` remains the only
  API that authorizes active/superseded executable policy use. Workflow authoring must not add a
  second YAML parser or infer kind from family names.
- Every dependency contains exactly `path`, `role`, and optionally `pinned`; paths are unique, role
  is `normative` or `reference`, `pinned` is a boolean allowed only for reference dependencies, and
  normative dependency digests remain release-evidence output rather than caller metadata.
- Input `authoring_basis` contains exactly `mode` and `confirmed_decisions`. Mode is
  `repository-source`、`pasted-source`、`guided`, or `accepted-changes`; decisions are an ordered list
  of unique, non-empty UTF-8 strings. `repository-source` and `pasted-source` require `--source`;
  `guided` forbids it. Initial family creation forbids `accepted-changes`.
- Persisted version metadata replaces that input object with exactly `mode`、`confirmed_decisions`、
  `source_path`、`source_commit`, and `source_sha256`. Computed source fields are null when not
  applicable; repository source path is normalized repo-relative, complete commit is recorded only
  when it actually contains the supplied bytes, and any supplied source has an exact 64-hex digest.
- `--source` is a regular non-symlink read-only input containing the exact pre-transformation source.
  For `repository-source` it must be inside the repository; for `pasted-source` it may be a temporary
  extracted input. The service, not caller JSON, computes the normalized audit-provenance object and
  persists it as version README frontmatter while rendering the same facts in the human-readable
  `Authoring basis` block: mode、repository-relative source path when applicable、current complete
  source commit when tracked、exact source SHA-256 when supplied and confirmed decision summary. A
  tracked source with index/worktree drift records the exact worktree digest and does not falsely
  claim that the commit contains those bytes. Task 7 release evidence copies and pins this normalized
  object; the prose block is not a second authority.
- Repository-relative metadata paths must be normalized, contain no `..`, resolve inside the
  repository root, and may not traverse symlinks.
- `--metadata` and `--definition` must be regular, non-symlink input files. Definition bytes are
  UTF-8 Markdown without YAML frontmatter or scaffold tokens; the service copies only their bytes
  into the allocated version.
- The repository allocates and writes workflow, title, version, definition, supersedes, and
  source-change identity fields; callers cannot provide or override them.

`change create --document` accepts UTF-8 Markdown with exactly substantive `Proposal` and `Impact`
sections and no frontmatter. The service creates the four-section schema-v2 document, leaving
`Validation` and `Decision` empty in the initial `proposed` record.

Exact slug collision is a repository error. Similar-family discovery remains an Agent semantic
responsibility performed before mutation; it is not implemented as a fuzzy repository-service
rule. When the confirmed result is a derived family, the exact `derived_from` object records that
decision.

- [ ] Write failing tests for exact slug collision, missing/unknown/wrongly typed metadata,
  duplicate capabilities/policy families/dependency paths, policy version/path/digest mismatch,
  unknown capability, missing/duplicate/extra required policy kind, invalid draft-policy null
  digest, invalid derived lineage, caller-supplied identity fields,
  source-mode/input mismatch, source provenance digest/commit rendering, YAML/frontmatter or symlink
  inputs, path escape, missing/extra change-body headings, scaffold tokens, stale indexes, and failed
  transaction recovery.
- [ ] Add focused policy-authoring/resolver tests for closed config keys、known kind values、draft
  inspection、identity/path mismatch, and the boundary that `inspect_registered()` does not make a
  draft executable through `resolve()`.
- [ ] Move every capability constant、supported-set check and capability-to-behavior lookup into
  `workflow_capabilities.py`; update authoring、study service、qualification and CLI consumers in the
  same PR. Add an `rg`-based test/assertion that rejects hard-coded maintained capability literals
  outside the canonical module and explicit legacy fixtures.
- [ ] Keep workflow semantic completeness out of structural CLI tests. Add Agent/fixture review
  scenarios that check all 11 contract concerns even when headings are translated; CLI tests cover
  only machine-verifiable bytes/schema/identity rules.
- [ ] Make `create_initial_draft()` allocate exactly `v001`. Under the Task 3 lock, reject the slug
  if the shared fail-closed identity scanner finds that family/version in registry、disk、any
  canonical current/historical path or textual reference; propagate non-Git/shallow/timeout/error
  proof failures and report collision/governance repair instead of
  silently creating an initial `v002`. Stage the complete version directory, service-rendered README
  including Authoring basis, registry draft entry, and indexes, then validate and publish all state
  as one logical mutation.
- [ ] Make `create_change()` resolve the unique active version and allocate the next never-used
  local `Cxxx` from the same reservation universe and lock, construct schema-v2 `CHANGE.md`, sync,
  validate, and publish through the Task 3 transaction coordinator.
- [ ] Add end-to-end concurrent create/change tests proving the shared lock and reservation scanner
  cannot allocate the same v001/Cxxx; Task 6 adds the equivalent evolve race.
- [ ] Default a complete confirmed change to `proposed`; keep human acceptance as a separate
  guarded transition.
- [ ] Ensure failures leave the exact pre-operation registry, indexes, directory inventory, and
  file bytes unchanged.
- [ ] Preserve current low-level commands for compatibility and diagnosis.
- [ ] Update CLI help and `CLAUDE.md` so the happy path no longer instructs Agents to copy assets,
  edit the root registry, or invoke sync separately.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring.py tests/test_workflow_studies.py \
  tests/test_study_qualification.py
uv run pytest tests/test_policy_authoring.py tests/policies/test_policy_resolver.py
uv run trading workflow validate --all
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: a complete new-family draft or proposed change is created without manual ID allocation,
template replacement, registry editing, index synchronization, or partial-state cleanup.

## Task 6: Add atomic next-version creation and in-place update

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `.agents/skills/trading-author-workflow/references/evolve.md`
- Modify: `.agents/skills/trading-author-workflow/references/impact.md`
- Modify: `CLAUDE.md`
- Modify: `docs/ARCHITECTURE.md`

**Repository interface:**

- `WorkflowRepository.create_replacement_draft(...) -> Path`

**CLI happy path:**

```bash
uv run trading workflow evolve <active-version-path> \
  --definition <complete-replacement-workflow-md> \
  --metadata <replacement-metadata.json> [--source <original-source>] [--update]
```

Without an existing family draft, the service allocates the next never-used local `vNNN`, selects
the complete set of accepted source changes, and records `supersedes`. If exactly one registered
replacement draft already exists, `--update` replaces that draft's complete definition and mutable
draft metadata in place while preserving its version identity. Calling without `--update` fails
before mutation so an Agent cannot accidentally overwrite reviewed draft work.

Replacement metadata is strict JSON with exactly `schema_version`, `capabilities`, `policies`,
`dependencies`, and `authoring_basis`, using the same closed item schemas, null/digest rules,
source-mode contract, and path boundaries as Task 5. `accepted-changes` is valid here and derives
provenance from the complete exact `source_changes`; it forbids `--source`. Repository/pasted source
modes require `--source`, while guided mode forbids it. Workflow, version, supersedes, derived
lineage, definition name, and `source_changes` are repository-derived and cannot be supplied by the
caller. `--definition` has the same UTF-8, no-frontmatter, no-symlink, and no-scaffold-token contract
as initial creation.

For a new replacement draft, the service renders the version's complete Authoring basis from the
input and accepted change set. `--update` deliberately replaces the mutable draft's prior
Authoring-basis block and confirmed-decision summary with the newly supplied basis; it never carries
old supplementary-source provenance implicitly. The immutable family `derived_from` lineage is
preserved, and the complete accepted `source_changes` set is regenerated. Because the target remains
a draft, the transaction journal supplies rollback history; superseded draft text is not promoted to
permanent released evidence.

- [ ] Write failing tests for no accepted changes, omitted accepted changes, unresolved draft or
  proposed changes, accidental overwrite without `--update`, update of the wrong/non-draft version,
  version-number reuse including historical-content references, metadata identity override,
  missing/unknown/wrongly typed schema fields, invalid capabilities/policies/dependencies,
  source-mode/input mismatch, path/symlink escape, and structurally invalid replacement inputs.
- [ ] Write passing tests proving `--update` retains the existing draft version number, refreshes
  the complete accepted `source_changes` set, applies the explicit Authoring-basis replace semantics,
  preserves immutable derived lineage, updates generated indexes, and does not alter the active
  version or its studies.
- [ ] Preserve the rule that every substantive v002+ rule must trace to accepted source changes;
  Agent semantic review remains required even when structural assembly is automated.
- [ ] Permit multiple accepted changes to feed one replacement draft. The skill must present
  combined impact analysis before draft write/update and again before release preparation; CLI
  verifies source-change identity/status but does not guess semantic coverage.
- [ ] Do not end or migrate old studies while creating a draft; version-boundary safety remains a
  release-time check because the active version is still authoritative.
- [ ] Publish replacement create/update, registry bytes, and generated indexes through the Task 3
  journal so exceptions and process restarts deterministically recover the selected before/after
  state.
- [ ] Add concurrent evolve/evolve and evolve/change tests proving version allocation、draft update
  and accepted-change refresh remain serialized without lost updates.
- [ ] Ensure abandoning a replacement draft does not recycle its version number.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring.py tests/test_workflow_identity.py \
  tests/test_policy_authoring.py tests/policies/test_policy_resolver.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: modifying a workflow requires one accepted change set and one complete replacement
contract, without manual version allocation, copying, registry edits, or source-change wiring.

## Task 7: Add persisted version-boundary authorization and consumption

**Files:**

- Create: `src/trading/core/workflow_release.py`
- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/core/workflow_studies.py`
- Modify: `src/trading/core/study_qualification.py`
- Modify: `src/trading/research_definitions/execution.py`
- Modify: `src/trading/cli.py`
- Create: `tests/test_workflow_release.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `tests/test_workflow_studies.py`
- Modify: `tests/test_study_qualification.py`
- Modify: `tests/test_qualification_workflow.py`
- Modify: `tests/test_workflow_native_research_cli.py`
- Modify: `.github/workflows/lint.yml`
- Modify: `.agents/skills/trading-author-workflow/references/evolve.md`
- Modify: `.agents/skills/trading-author-workflow/references/impact.md`
- Modify: `.agents/skills/trading-author-workflow/references/release.md`
- Modify: `.agents/rules/workflow-version-boundary.md`
- Modify: `CLAUDE.md`
- Modify: `docs/ARCHITECTURE.md`

**Replacement disposition input:**

```json
{
  "schema_version": 1,
  "source_version_path": "workflows/example--v001",
  "target_version_path": "workflows/example--v002",
  "studies": [
    {
      "source_study_path": "workflows/example--v001/work/studies/example--s001",
      "action": "restart"
    }
  ]
}
```

The object and each study item use exactly the shown keys. Study paths are unique, ordered,
repository-relative, regular directories under the exact source version; action is `continue`、
`restart`, or `close-invalidated`. Every paused source study appears exactly once, while completed/
cancelled studies are absent. Initial release forbids this input. Every replacement release requires
the file even when no paused study exists; that case supplies an empty `studies` list, eliminating an
ambiguous omitted-input branch.

**Repository and CLI contract:**

- `WorkflowRepository.release(version_path: Path, *, approved_by: str, dispositions_path: Path | None) -> Path`

```bash
uv run trading workflow release <version-path> \
  --approved-by <human-id> [--dispositions <replacement-dispositions.json>]
```

The service, not the parser, enforces that initial release must omit `dispositions_path` and every
replacement release must provide it. Both the existing command and skill happy path dispatch to this
one method; no lower-level release writer accepts an already-normalized mapping or bypasses the
file's closed-schema/path checks.

**Release schema v2:**

- All new release writes use schema version 2. Its exact top-level keys are the existing schema-v1
  keys `approved_at`、`approved_by`、`capabilities`、`dependencies`、`derived_from`、`policies`、
  `prepared_at`、`schema_version`、`source_changes`、`supersedes`、`version`、`workflow`、
  `workflow_sha256`, plus `authoring_basis`、`authoring_basis_sha256`、
  `source_change_evidence`, and `study_dispositions`.
- `authoring_basis` is the exact normalized audit-provenance object persisted by the version README;
  `authoring_basis_sha256` hashes its canonical JSON serialization. Release validation rejects any
  later basis drift while allowing guarded draft updates before release.
- `source_change_evidence` is ordered one-to-one with `source_changes`. Each item contains exactly
  `path`、`format`, and `files`; `files` is the sorted complete authority manifest of exact
  repository-relative file paths and SHA-256 values. Legacy entries pin README/PROPOSAL/IMPACT/
  VALIDATION/DECISION. Schema-v2 entries pin terminal `CHANGE.md` and every add-only decision-event
  sidecar. Missing/extra/reordered paths、event deletion or digest drift invalidate release evidence.
- `study_dispositions` is the normalized ordered array from the guarded input; each item contains
  exactly `source_study_path`、`action`, and `target_version_path`. Target path always equals the
  released replacement; it is retained even for close-invalidated so the boundary identity is
  explicit. The release SHA-256 makes the authorization immutable.
- Existing schema-v1 releases remain readable without migration. Absence of `study_dispositions` in
  schema v1 means “no new machine-consumable cross-version authorization”; it does not invalidate
  historical studies or permit a new cross-version revisit.
- `workflow_release.py` owns the only closed-schema v1/v2 parser and normalized release model.
  Authoring validation、`WorkflowStudyService`、workflow-native execution、research CLI、study
  qualification and qualification workflow import it instead of checking schema numbers or keys
  independently. Execution resolves the same exact policy pins for v1 and v2; the shared parser
  rejects unknown governance fields before any consumer uses the release.

**Revisit branches:**

- Same-version revisit: when source and target study workflow-version paths are identical, source
  status must be `draft`、`cancelled` or `completed`. This preserves draft redesign、cancel/recreate
  and completed follow-up without allowing two open preregistered/running/paused/awaiting-review
  branches. No release disposition or consumption artifact is required; new metadata records null
  action/consumption.
- Direct cross-version revisit: when paths differ, the exact active target release must authorize the
  exact source study with continue/restart. Close-invalidated、missing、wrong-target or schema-v1
  absence fail closed.
- `continue` and `restart` both require an exact `paused` source and a new target preregistration.
  `continue` additionally pins the source `PREREGISTRATION.json` and frozen hypothesis digest in the
  consumption artifact; target preregistration fails unless its `HYPOTHESIS.md` bytes have that exact
  digest. Its plan、execution and evidence are new under the replacement workflow. `restart` records
  source identity but permits a new hypothesis and plan and begins with no carried evidence.
- After a consumed cross-version handoff, later same-version redesigns under the target version use
  the same-version branch and revisit the newest study; they do not consume the old boundary again.
- Repository validation treats `revisits` as a directed graph, requires every path to exist and stay
  in the same workflow family, and rejects self-reference or cycles. Manual metadata edits cannot
  manufacture a circular continuation chain.

**Study metadata and durable consumption:**

- After Task 7, every newly written study README includes `revisit_action`、
  `disposition_consumption`, and `disposition_consumption_sha256`, each null for no/same-version
  revisit. For an authorized cross-version revisit they equal the release action、exact consumption
  artifact path and its 64-hex digest. Studies pinned to a schema-v2 workflow release must contain
  all three keys. Studies already pinned to schema-v1 releases may omit all three as legacy-compatible
  bytes; the post-Task-7 writer still emits null fields for new same-version studies under those
  releases and never rewrites old studies.
- Cross-version init atomically creates the study directory、generated index changes and an add-only
  consumption artifact at
  `<target-version>/work/disposition-consumptions/<sha256(source-study-path + NUL + target-version-path)>.json`.
  The artifact has exactly `schema_version`、`source_study_path`、`source_version_path`、
  `target_version_path`、`action`、`authorization_release_path`、
  `authorization_release_sha256`、`source_preregistration_sha256`、
  `source_hypothesis_sha256`、`created_study_path`、`consumed_at`, and `consumed_by`. The two source
  digests are required 64-hex for `continue` and null for `restart`.
  Time is writer-generated current UTC; actor is the stable study initializer identity. Caller input
  cannot provide either field or the artifact digest.
- The deterministic artifact key is the single-use authority. Init before commit decision that
  fails/rolls back creates neither study nor consumption; commit-decided recovery rolls both forward.
  Once committed, cancellation or deletion of the created study never releases authorization.
  Deleting the study instead makes repository validation fail because the immutable consumption
  references a missing created path; there is no reclaim/reuse command.
- Validator requires one-to-one agreement among release mapping、consumption artifact、new study
  `revisits`/metadata/digest and target version. A source+target boundary has at most one consumption;
  artifact byte tampering fails the study's pinned digest.
- Non-dry-run qualification registration revalidates this agreement inside the shared workflow then
  qualification locks; a cross-version study with missing/drifted consumption can never register an
  outcome-relevant qualification plan.

- [ ] Add release parser/writer/validator tests for exact schema-v1/v2 closed keys、legacy schema-v1
  omission、complete paused-study coverage、wrong target、authoring-basis pin、complete source-change
  authority manifest and immutable release authorization digest.
- [ ] Add one real schema-v2 release fixture that passes `resolve_workflow_policy_set()`、workflow-
  native research CLI context construction and structured study/qualification runtime-contract
  checks. Prove v1 and v2 resolve identical policy sets and unknown/malformed v2 fields fail in every
  consumer through the shared parser.
- [ ] Extend the canonical CI focused command with `tests/test_workflow_release.py` and
  `tests/test_workflow_native_research_cli.py`; PR 5 must be independently green with a real v2
  active-release reader path, not rely on the later full-suite handoff.
- [ ] Add same-version、direct cross-version and cross-then-same-version revisit tests, plus missing/
  close/wrong-target authorization、graph cycle and cross-family rejection. Cover allowed same-version
  draft/cancelled/completed sources、rejection of all open outcome-relevant sources, and mechanical
  continue hypothesis equality versus restart freedom.
- [ ] Add atomic consumption tests for pre-decision rollback、commit-decided recovery、single-use,
  cancellation permanence、deleted-study invalidity and concurrent double-init.
- [ ] Update only the canonical version-boundary reference with these rules; impact/study governance
  references route to it without restating schemas or lifecycle logic.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_release.py tests/test_workflow_authoring.py \
  tests/test_workflow_studies.py \
  tests/test_study_qualification.py tests/test_qualification_workflow.py \
  tests/test_workflow_authoring_transaction.py tests/test_workflow_native_research_cli.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: version-boundary dispositions become durable, auditable, single-use machine authority
without changing same-version study redesigns or rewriting old study bytes.

## Task 8: Simplify abandon, retire, and deletion semantics

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/core/workflow_studies.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `tests/test_workflow_studies.py`
- Modify: `tests/test_qualification_workflow.py`
- Modify: `.agents/skills/trading-author-workflow/references/remove.md`
- Modify: `.agents/skills/trading-author-workflow/references/impact.md`
- Modify: `.agents/rules/workflow-version-boundary.md`
- Modify: `CLAUDE.md`
- Modify: `workflows/README.md`
- Create: `workflows/REGISTRY_MIGRATION.json`
- Modify: `docs/ARCHITECTURE.md`

**CLI aliases:**

```bash
uv run trading workflow registry migrate-v2 --by <stable-operator-id>

uv run trading workflow abandon <draft-version-path>
uv run trading workflow retire <active-version-path> \
  --dispositions <retirement-dispositions.json> \
  --reason <reason> --approved-by <human-id>

uv run trading workflow version transition <active-version-path> --to retired \
  --dispositions <retirement-dispositions.json> \
  --reason <reason> --approved-by <human-id>
```

`WorkflowRepository.migrate_root_registry_v2(*, migrated_by: str) -> Path` is a one-time guarded
transaction. It requires exact valid schema-1 input、no migration marker and the repository's empty
legacy-retirement set; it computes both registry digests、uses current UTC and publishes schema-2
registry plus marker atomically. It rejects caller timestamps/digests, a second migration, or any
schema-1 retired entry because this repository has no approved grandfathered omission.

The existing `workflow version transition` command remains available, but its retired branch now
requires exactly the same reason/disposition/approval inputs as the alias. Both parsers dispatch to
one evidence-producing repository method; there is no optional unsafe retirement path. The
`draft -> abandoned` branch rejects reason/disposition parameters. `abandon` is likewise only parser
sugar over that guarded branch.

**Retirement disposition contract:**

- `retirement-dispositions.json` has exactly `schema_version`、`version_path`, and `studies`.
  `schema_version` is 1; version path is the exact active version; studies is an ordered array whose
  items contain exactly `source_study_path` and `action`, with unique exact paused-study paths under
  that version and action always `close-invalidated`.
  Pure retirement is terminal: it has no replacement target and therefore rejects continue/restart
  spellings or target version/study paths. Continue/restart must use the Task 7 replacement-release
  disposition contract instead.
- Every paused study must appear exactly once; completed/cancelled studies must not appear. Unknown,
  duplicate JSON key/path, absolute, symlinked, outside-version, or status-mismatched paths fail
  closed.
- Successful retirement creates immutable schema-v1 `RETIREMENT.json` with exactly
  `schema_version`、`workflow`、`version`、`version_path`、`release_path`、`release_sha256`、
  `retired_at`、`retired_by`、`reason`, and `study_dispositions`. The final array repeats normalized
  items with exact source path and close-invalidated action.
- Task 8 atomically upgrades the root registry to schema version 2 before exposing retirement.
  Schema-v2 non-retired version records retain exactly the existing keys and reject
  `retirement_evidence_sha256`; every `retired` record requires that additional key with the exact
  64-hex digest of its `RETIREMENT.json`. Missing/null evidence is never a valid schema-v2 retired
  state. The repository currently has no retired entries, so its closed grandfather allowlist is
  empty and no omission branch exists.
- The same transaction creates add-only `workflows/REGISTRY_MIGRATION.json` with exactly
  `schema_version`、`from_schema`、`to_schema`、`before_sha256`、`after_sha256`、`migrated_at`, and
  `migrated_by`; it pins the before/after root-registry bytes and the current-time stable actor.
  Schema-v1 parsing exists only as input to this guarded migration and frozen legacy parser fixtures.
  Once this marker exists—or the complete Git path-history proof shows it was ever tracked—
  `validate --all`、sync and every mutation reject a missing/changed marker or root-registry downgrade.
  No ordinary CLI can add a grandfathered record or expand an allowlist. This provides a mechanical
  boundary instead of interpreting field absence as both legacy and illegal new retirement.
- `RETIREMENT.json` is add-only and digest-pinned. Retirement does not modify the released
  `WORKFLOW.md` or existing `RELEASE.json`; validation treats later retirement evidence as separate
  lifecycle evidence rather than a rewrite of release bytes.
- Retirement dispositions are normative close authorizations. Old studies remain historically
  paused, but `WorkflowStudyService.initialize()` and repository validation reject every future
  `revisits` chain that names a study closed by immutable retirement evidence.
- The canonical version-boundary reference owns this schema and closure rule. Remove/impact mode
  references only route to it; they do not duplicate the normative content.
- Retirement artifact, registry transition, indexes, and disposition validation publish through
  the Task 3 transaction coordinator.

- [ ] Add parser and dispatch tests for one-time `registry migrate-v2`、`abandon`、`retire`, and both branches of
  `version transition`, including no-backdated-clock, closed disposition-input schema, required
  retirement evidence args, rejection of the old bypass form, and rejection of retirement-only args
  on abandon.
- [ ] Prove the alias and low-level retired form produce byte-identical `RETIREMENT.json`, registry,
  and index state through the same repository method.
- [ ] Prove `retire` still requires a stable human identifier, no blocking changes, and safe study
  states.
- [ ] Prove retirement refuses missing/extra/duplicate/wrong-status disposition paths and that a
  successful `RETIREMENT.json` covers every paused study one-to-one with only
  `close-invalidated`; explicitly reject continue/restart and any claimed replacement target.
- [ ] Prove artifact, registry digest, lifecycle state, and indexes recover together across injected
  failures and a fresh process restart.
- [ ] Add root-registry schema 1 -> 2 migration、schema downgrade、missing/null/malformed retirement
  digest、missing/changed/historically-deleted migration marker and hand-edited active-to-retired
  bypass tests. Prove the current empty grandfather set cannot be extended through metadata or CLI
  input.
- [ ] Prove `abandon` accepts only a registered draft and permanently retains its registry entry.
- [ ] Prove superseded, retired, abandoned, or released versions cannot be physically deleted by
  either command.
- [ ] Keep unregistered local-draft deletion outside the generic CLI. The skill must show the exact
  path and use the shared identity scanner to prove it is absent from every canonical current/
  historical path and textual reference. Non-Git、shallow、timeout/error or incomplete-history proof
  fails closed. The skill resolves current Git status, warns about recoverability, and obtains
  separate explicit confirmation before direct deletion. If it was ever tracked or referenced,
  refuse physical deletion and leave the path untouched; this plan does not invent an implicit
  tombstone/adoption mutation. If such a path is already missing, the Task 3 historical reservation
  scan still permanently blocks identity reuse and reports governance repair.
- [ ] Prove an ever-tracked/referenced unregistered path is refused without mutation, and that an
  already-missing historical identity still blocks create/evolve allocation. A future
  adopt-as-abandoned repair API is outside this simplification unless separately designed and
  approved.
- [ ] Ensure the skill reports whether the user's word “delete” was resolved to local deletion,
  abandon, retire, or refusal.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring.py tests/test_workflow_studies.py \
  tests/test_qualification_workflow.py tests/test_workflow_authoring_transaction.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: users can ask to remove a workflow without first knowing lifecycle vocabulary, while the
repository preserves every registered or released historical identity.

## Task 9: Full history-compatible verification and handoff

**Files:**

- Verify all files changed in Tasks 1–8.
- Modify: `docs/ARCHITECTURE.md`
- Modify: `CLAUDE.md`
- Modify: `workflows/README.md`
- Modify: `.agents/skills/trading-author-workflow/agents/openai.yaml`
- Delete after all callers migrate: `.agents/skills/trading-author-workflow/assets/change/` legacy
  authoring templates; legacy workflow change records remain untouched and readable
- Do not modify existing `workflows/**/WORKFLOW.md`, `RELEASE.json`, studies, or legacy changes.

- [ ] Confirm `git diff` contains no changes beneath any existing released workflow version.
- [ ] Confirm v008/C001 remains readable in its legacy five-file format and retains its exact
  lifecycle state.
- [ ] Run:

```bash
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-author-workflow
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-operate-workflow
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-evaluate-study
uv run pytest tests/test_workflow_release.py
uv run pytest tests/test_workflow_authoring.py
uv run pytest tests/test_workflow_authoring_transaction.py
uv run pytest tests/test_workflow_identity.py
uv run pytest tests/test_workflow_studies.py
uv run pytest tests/test_study_qualification.py
uv run pytest tests/test_qualification_workflow.py
uv run pytest tests/test_workflow_native_research_cli.py
uv run pytest tests/test_policy_authoring.py tests/policies/test_policy_resolver.py
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
git diff --check
git status --short
```

- [ ] Exercise an isolated temporary repository through these scenarios:
  1. create and validate a new v001 draft from a complete definition with exactly the four required
     policy kinds and only supported capabilities; reject missing/duplicate kinds and unknown
     capability;
  2. create a schema-v2 change, defer/repropose it more than once, replay every exact decision
     snapshot/event, then accept it; separately exercise explicit withdrawal and prove rewriting
     CHANGE plus all in-file digests cannot bypass the add-only event anchor;
  3. aggregate two accepted changes into one replacement draft;
  4. accept another change and update the same replacement draft identity in place;
  5. abandon a draft and prove registry、all canonical path/text references、complete Git path/blob
     history、stage-0 index and concurrent allocation cannot reuse its number; prove shared-blob
     multiple paths、unmerged index、non-Git、shallow and Git-error cases fail closed for v/C/S;
  6. preserve the exact allowed same-version source-state matrix without disposition, then release a
     schema-v2 replacement with typed exact-target dispositions and prove workflow-native execution/
     qualification can read it; atomically consume each cross-version continue/restart exactly once,
     enforce their different hypothesis rules, preserve consumption after cancellation/deletion, and
     reject close/missing/wrong-target/cyclic revisits;
  7. atomically migrate the root registry to schema 2, then separately retire an active workflow
     through both alias and low-level command; prove byte-identical evidence and reject schema
     downgrade、marker removal、the old no-reason/no-disposition bypass plus open/incomplete cases;
  8. race study init/resume/sync and non-dry-run qualification registration against release、
     retirement and completion, proving the shared lock and in-lock precondition reread preserve the
     version boundary;
  9. crash at every transaction phase and immediately invoke every study writer, proving the common
     pending-journal gate recovers first or writes nothing; verify workflow-before-qualification lock
     ordering;
  10. inject external target and validation-read-set changes before commit decision and between
      publications, proving CAS behavior、prepared cleanup/abort、commit-decided roll-forward、complete
      cleanup、fresh-process status/recover and fsync ordering; prove post-decision non-target drift
      reports invalidity without retaining a completed journal;
  11. validate a mixed repository containing legacy and schema-v2 changes;
  12. verify legacy index links and schema-v2 direct `CHANGE.md` links.
- [ ] Perform read-only skill behavior checks for review, create, evolve, remove, and release modes;
  verify each loads every reference required by its specific object/impact and forbids unrelated
  references, without inferring mutation or approval. Repeat final routing checks for author、operate
  and evaluate callers rather than relying only on Task 2 validation.
- [ ] Confirm documentation describes only the new happy paths while retaining compatibility notes
  for low-level legacy commands.
- [ ] Update `workflows/README.md` human-facing routing so review、create、evolve、abandon、retire 與
  release paths match the revised skill/CLI while leaving registry frontmatter authority unchanged.
- [ ] Delete legacy skill assets only after `rg` proves no maintained writer/caller references them;
  retain permanent legacy on-disk reader coverage in tests.

Expected: the simplified authoring experience is additive and deterministic; the one root-registry
schema migration is explicit and atomic, while every existing workflow、release、study and legacy
change byte remains fully compatible without per-object migration.

## Completion criteria

The plan is complete only when all of the following are true:

- A normal review does not load unrelated create/evolve/remove/release instructions.
- `trading-operate-workflow` and `trading-evaluate-study` load the canonical study-governance
  reference without depending on deleted/moved authoring-mode details.
- Author impact and study revisit flows share one canonical version-boundary reference without
  duplicating its rules or loading unrelated authoring modes.
- Existing and new authoring writes recover deterministically across exceptions, process restart,
  and the documented host/filesystem crash model under one durable journal; all study writers share
  the same mutation-entry gate, recover/reject pending journals first, follow workflow-before-
  qualification lock ordering, and re-read lifecycle preconditions inside the lock.
- Non-dry-run qualification registration uses the same workflow-before-qualification gate and can
  proceed only for an active running study with valid version-boundary consumption where applicable.
- Commit decision requires a full before-state CAS recheck; publication never overwrites a target
  whose kind/mode/digest moved outside the recorded before/after states.
- WAL records and CAS-checks every assert-only validation input that determines after-state.
  Post-decision non-target drift may fail repository health validation but cannot permanently retain
  an otherwise complete journal.
- Prepared recovery never writes canonical targets, commit-decided recovery only rolls forward, and
  complete recovery only cleans up; an explicit audited abort exists only for prepared operations.
- A complete new workflow can reach a validated v001 draft without manual ID allocation, template
  copying, registry editing, sync invocation, or partial cleanup.
- A new family is always `v001`; any same-slug registry/path/current-or-historical reference is a
  collision or governance-repair condition, never permission to create an initial `v002`.
- A new change uses exactly one author-edited `CHANGE.md`; only guarded decisions add generated,
  content-addressed event sidecars. It retains proposal、impact、validation、decision and release
  semantics while providing an external immutable audit anchor.
- Deferred/reproposal history preserves replayable exact Validation/Decision snapshots with legal
  event sequence and timestamps; withdrawal has one explicit guarded CLI path.
- A replacement draft is allocated and wired from all accepted changes atomically.
- Later accepted changes update the same registered replacement draft identity instead of consuming
  another version number.
- A user can abandon or retire through direct commands without weakening human approval or study
  safety.
- Replacement release persists typed dispositions with the exact target version. Terminal
  retirement persists immutable evidence that covers every paused study exactly once as
  `close-invalidated` and never promises continuation/restart.
- Continue/restart authorization is enforced and single-use at study initialization;
  consumption is durable even if the created study is cancelled/deleted, and close-invalidated
  studies cannot be revisited, while their historical paused bytes remain intact. Same-version
  cancel/recreate revisits remain valid without a release disposition.
- `retire` and `version transition --to retired` use one evidence-producing method; neither provides
  a reason/disposition bypass.
- Root registry schema 2 and its add-only migration marker make every new retired state require an
  exact retirement-evidence digest; schema downgrade or a newly omitted digest fails closed.
- Existing v001–v008 workflows, releases, studies, and legacy changes validate without migration.
- No registered or released workflow history is physically deleted.
- Never-used allocation includes registry、disk、inbound references、complete Git path history、
  de-duplicated historical blob content、stage-0 index and concurrent reservations. Grammar preserves
  per-version scoping; path proof never relies on the optional path attached to a de-duplicated blob,
  and ref/index/inventory proof tokens are CAS-checked before commit. Non-Git、shallow、unmerged-index、
  timeout or Git-error proof fails closed for v/C/S IDs.
- Initial/replacement metadata has one closed schema, preserves service-verified authoring
  provenance, and defines capability/policy/dependency types, uniqueness, and draft null-digest
  behavior.
- New authoring rejects unknown capabilities, and release resolves exactly one market、broker、
  execution and portfolio-risk policy kind through the authoritative policy inspector; legacy
  workflow bytes remain migration-free.
- Schema-v2 change metadata rejects unknown/stale decision state and preserves deferred/reproposal
  history through append-only, byte-replayable decision snapshots and content-addressed event anchors;
  schema-v2 release pins the complete terminal source-change authority manifest.
- Schema-v2 release is accepted by the same closed dual-schema parser in authoring、workflow-native
  execution、research CLI and qualification consumers, and pins normalized authoring provenance.
- All focused tests, full tests, Ruff, skill validation, workflow validation, and diff checks pass.

## Explicitly deferred work

- Moving the root registry out of `workflows/README.md` frontmatter.
- Removing legacy five-file change parsing.
- Rewriting existing changes into schema v2.
- Removing existing low-level transition/sync commands.
- Adding a generic destructive `workflow remove` CLI.
- Adding a lifecycle that revives a retired workflow family.
- Adding an adopt/register-tombstone repair API for unregistered historical drafts.
- Changing unrelated study lifecycle states, approvals, evaluation, completion, qualification,
  Shadow, activation, or trading authority. Tasks 3 and 7 only add the shared mutation gate,
  lock-order correction, and enforcement of version-boundary disposition authority; they do not
  alter frozen plans, evidence, outcomes, or existing study bytes.
- Releasing or retiring any actual repository workflow as part of the authoring-tool improvement.

## Recommended merge sequence

Keep each step independently reviewable and do not begin later happy-path CLI work until the prior
foundation is merged and green:

1. **PR 1 — Skill routing compatibility:** Tasks 1–2 only. Add progressive disclosure, retain the
   compatibility pointer, and update author/operate/evaluate callers.
2. **PR 2 — Transaction and identity foundation:** Task 3 only. Add the common pending-journal gate,
   workflow-before-qualification lock ordering, bounded WAL target operations, target/read-set CAS,
   cached fail-closed v/C/S identity proof; retrofit sync、transitions、release and study writers
   without adding schema-v2 or create/evolve commands yet.
3. **PR 3 — Change schema v2:** Task 4 only. Add normalized dual reader、direct index targets、
   replayable decision snapshots、content-addressed add-only event anchors、`change decide`, and
   explicit `change withdraw`; keep legacy assets until final caller verification. This PR does not
   expose `change create` yet.
4. **PR 4 — Draft authoring happy paths:** Tasks 5–6. Add `change create`, strict closed metadata and
   authoring provenance, supported-capability/four-policy validation, exact-v001/never-used
   allocation, replacement draft creation, and in-place `--update`; do not enable version-boundary
   authorization yet.
5. **PR 5 — Persisted version-boundary authorization:** Task 7 only. Add the shared dual-schema
   release parser before any v2 write、source-change/provenance pins、exact same/cross-version revisit
   branches、add-only durable consumption and cycle/single-use validation.
6. **PR 6 — Lifecycle UX and history-compatible verification:** Tasks 8–9. Atomically migrate the
   root registry to schema 2 with an add-only marker, add retirement evidence、safe low-level
   transition parity、abandon/retire aliases、documentation and forward tests, then remove obsolete
   writer assets only after inbound-link checks pass.
