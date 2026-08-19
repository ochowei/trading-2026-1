# Trading Workflow Authoring Simplification Implementation Plan

**Goal:** 簡化 `trading-author-workflow` 新增、修改與停止使用 repository workflow 的流程，
同時保留 released workflow immutability、human authority、study safety、release evidence 與既有
workflow/change history 的完整相容性。

**Architecture:** 先將 skill 改為 progressive disclosure，但保留舊 authoring-contract 路徑作
相容入口，並同步更新 study operation/evaluation callers。接著建立 crash-safe authoring
transaction substrate，再讓 repository 同時讀取 legacy 五檔 change records 與新的單一
`CHANGE.md`。所有既有與新增 authoring mutation，以及所有會寫入 `workflows/` 的 study mutation，
都共用 repository lock；authoring mutations 再透過 durable journal、shadow validation 與
deterministic recovery 發布。
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
  新 create/evolve）與每個 `WorkflowStudyService` write 都必須使用同一 repository-scoped lock。
  所有 writer 取得 lock 後必須先處理 pending authoring journal，再重讀 lifecycle preconditions；
  study writer 不得繞過 crash recovery gate。Authoring mutation 另使用 durable transaction
  protocol。捕捉到的 exception、process crash、host/power loss 或重新啟動後，不得留下不可判讀的
  partial state。Study lifecycle 語意不因此改變。
- `workflows/README.md` frontmatter 繼續作 lifecycle authority，不搬移 registry storage；只允許
  Task 7 為 retirement evidence 增加向後相容的 optional digest field。
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
2. **New writes use schema v2 only.** 新 change directory 只包含 `CHANGE.md`。
3. **No mixed representation.** 同一 change directory 同時出現 legacy 與 v2 authority 時，
   validation fail closed。
4. **Source-change paths remain directory paths.** Version metadata 與 release evidence 的
   `source_changes` 繼續指向 change directory，不因內部格式改變而破壞 lineage。
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
- [ ] Preserve repository precedence, immutable released workflow behavior, source disposition,
  study scope separation, and release authority.
- [ ] Update skill frontmatter `description` so review、create、evolve、abandon、retire 與 release
  都可被正確選擇；同步更新 default prompt，但不把 UI prompt 當成 discovery authority。
- [ ] Update both maintained study skills to the new study-governance reference, then use `rg` to
  verify no maintained caller still requires the monolithic contract contents.
- [ ] Run the skill validator:

```bash
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-author-workflow
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-operate-workflow
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
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
- Modify: `tests/test_workflow_authoring.py`
- Create: `tests/test_workflow_studies.py`
- Modify: `tests/test_study_qualification.py`
- Modify: `src/trading/cli.py`
- Modify: `CLAUDE.md`
- Modify: `.gitignore` only if the existing `state/` rule does not already cover the journal
- Modify: `docs/ARCHITECTURE.md`

**Lock and durability contract:**

- One repository-scoped filesystem lock serializes identity allocation, every authoring write, and
  every `WorkflowStudyService` mutation that writes under `workflows/`. The lock implementation
  supports an explicitly passed/re-entrant lease so a study mutation can call index sync without
  deadlocking or releasing the boundary midway.
- Every workflow writer uses one `enter_workflow_mutation()` invariant: acquire the shared lock;
  inspect the pending authoring journal; automatically execute the deterministic action already
  selected by a valid `prepared`/`commit-decided` phase; fail closed with the status/recover command
  for corrupt/foreign/conflicting journals; then re-read registry, exact version, study inventory,
  and caller-specific lifecycle preconditions. Release/retire cannot rely on a safe-study check made
  before the lock; study init/resume cannot rely on an active-version check made before the lock.
- Global lock ordering is `workflow repository lock -> qualification lock`. Study completion paths
  that also need qualification state must be refactored to acquire them in this order; no code path
  may acquire the qualification lock and then wait for the workflow lock.
- A transaction computes the complete post-state in memory, including registry bytes, generated
  root/version indexes, lifecycle metadata, release/change artifacts, directory creates, and any
  allowed deletions. Each target records its repository-relative path, before/after kind
  (`absent`, regular file, or directory), POSIX mode where relevant, exact SHA-256, recoverable
  before bytes, and staged after location. Symlink targets fail closed.
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
  6. compare-and-swap recheck every canonical target's kind、mode and digest against the recorded
     before-state. Any mismatch leaves canonical bytes untouched, retains `prepared`, and reports
     the conflicting path;
  7. durably replace the phase with `commit-decided` and fsync the journal parent;
  8. before publishing each still-unpublished target, confirm it still matches before-state; already
     published targets must match after-state. A third state fails closed instead of overwriting an
     editor/Git/uncoordinated writer change;
  9. publish each target idempotently, fsync every written file and affected parent directory, then
     verify exact after kinds/modes/digests;
  10. run full canonical validation, durably mark `complete`, and only then remove journal/staging
     bytes and fsync their parents.
- A local-only journal under `state/workflow-authoring/` stores schema version, repository identity,
  operation ID/type, complete target manifest, before/after values, staged paths, and phase.
  `prepared` recovery restores the exact before-state; `commit-decided` recovery rolls forward the
  exact after-state. If any canonical target matches neither its recorded before nor after state,
  recovery fails closed and reports the exact conflicting path.
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
- `WorkflowRepository.authoring_transaction_status()`
- Shared `WorkflowRepositoryMutationLock` lease used by `WorkflowRepository` and
  `WorkflowStudyService`.

**Operational CLI:**

```bash
uv run trading workflow authoring status
uv run trading workflow authoring recover
```

`status` is read-only. `recover` requires the shared lock and only applies the phase already durably
recorded; it never accepts replacement operation inputs or a caller-selected rollback direction.
Normal authoring and study writers automatically recover a valid journal through the same mutation
entry invariant; explicit `recover` exists for diagnosis/retry after an operator has resolved a
reported conflicting target. Corrupt or conflicting journals are never auto-rewritten.

**Identity proof contract:**

- `workflow_identity.py` provides one fail-closed reservation scanner for `vNNN`、`Cxxx`, and
  `Sxxx`. It searches current registry/filesystem plus every locally reachable commit/ref using:
  exact `workflows/<slug>--vNNN` and `<slug>--vNNN` paths; canonical `<slug>@vNNN`; exact change
  directory paths/basenames; canonical `<slug>@vNNN/Cxxx`; and local `Cxxx` references only in
  documents structurally scoped/pinned to that source version. Study reservation likewise covers
  exact study paths/basenames and `<slug>@vNNN/Sxxx` or version-scoped `Sxxx` references.
- Non-Git worktrees, `git rev-parse --is-shallow-repository == true`, command timeout/non-zero,
  unreadable objects, or inability to enumerate `git rev-list --all` fail closed with an actionable
  “cannot prove never-used” error. No exception/timeout is converted to an empty history result.
- The guarantee covers complete locally reachable `--all` history; canonical CI performs the same
  check in a non-shallow clone. Allocation does not claim knowledge of commits never fetched into
  any local ref.

- [ ] Write failing tests for exclusive/re-entrant lease behavior, exact path kind/mode/absence and
  before/after plans, staged shadow validation with real-index mapping, rollback before commit
  decision, roll-forward after commit decision, corrupt journal, wrong repository identity,
  changed staged bytes, a canonical target matching neither digest, orphan staging, idempotent
  recovery, and incompatible retry.
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
- [ ] After a crash at every prepared/commit-decided/publication phase, immediately invoke each
  study writer and prove it first completes the selected authoring recovery or fails without writing.
- [ ] Add reservation tests for all canonical path/text spellings, version-scoped local IDs,
  non-Git/shallow repositories, Git timeout/non-zero, missing objects, and `Sxxx` historical/inbound
  references; preserve permanent local scoping between unrelated workflow versions.
- [ ] Add parser/dispatch tests for `workflow authoring status/recover`, including clean state,
  prepared rollback, commit-decided roll-forward, corrupt journal refusal, and read-only status.
- [ ] Retrofit existing authoring mutations before adding new schema-v2 writers or happy-path CLI.
- [ ] Replace Task 1 characterization expectations with crash-safe assertions once the coordinator
  is active.
- [ ] Keep the journal local-only and free of credentials, broker exports, private ledgers, market
  outcomes, or other trading data.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring_transaction.py tests/test_workflow_identity.py \
  tests/test_workflow_authoring.py tests/test_workflow_studies.py tests/test_study_qualification.py
uv run trading workflow validate --all
```

Expected: every existing authoring mutation is serialized and recoverable across exceptions,
process restarts, and the documented filesystem crash model; study writers share the same safe
version boundary before new create/evolve behavior is introduced.

## Task 4: Add schema-v2 single-file change records

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Retain temporarily: `.agents/skills/trading-author-workflow/assets/change/` legacy five-file assets
- Create: `.agents/skills/trading-author-workflow/assets/change-v2/CHANGE.md`
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

- All schema-v2 files always contain exactly the four headings `Proposal`, `Impact`, `Validation`,
  and `Decision` in that order.
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
  `validation_sha256`, `decision_sha256`, and `snapshot_sha256`. Status is `accepted`、`rejected`、
  `deferred`, or `withdrawn`; withdrawal has null `validation_sha256`, while all other digests are
  exact 64-hex values. Sequence begins at 1 without gaps, timestamps are canonical current-time UTC
  and strictly increase, and frontmatter items must exactly match the generated snapshots in the
  Decision section.
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

`change decide` writes the latest Validation body, appends an exact Validation/Decision snapshot,
and publishes lifecycle metadata/history in one authoring transaction. `change withdraw` appends an
exact withdrawal snapshot and publishes withdrawn metadata in one transaction; it records an actor
but is not human approval of a research decision. The legacy low-level `change transition` remains
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
  timestamp/sequence ordering, exact snapshot replay, tampered snapshot/digest rejection, and release.
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
- [ ] Keep legacy assets until the schema-v2 writer and all maintained skill callers pass Task 8
  verification. New writes use only `assets/change-v2/CHANGE.md` and never copy unfinished tokens
  into a proposed change.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring.py
uv run trading workflow validate --all
```

Expected: old bytes remain authoritative and valid; new changes use one file and have equivalent
lifecycle, impact, decision, release, and audit semantics.

## Task 5: Add atomic change creation and workflow draft creation

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Create: `src/trading/core/workflow_capabilities.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
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
  `WorkflowStudyService` imports the same registry for behavior gates. Permanent legacy readers do
  not rewrite or retroactively reject already released/superseded/retired historical bytes solely
  for an unknown legacy capability, but every draft entering the new release path must use supported
  values.
- Every policy item contains exactly `family`, `version`, `path`, and `release_digest`; family values
  are unique lowercase kebab-case identities, version/path must agree with the policy registry, and
  duplicate policy families fail closed. `release_digest` is either the exact 64-hex digest of a
  released policy's `RELEASE.json`, or null only while both the selected policy and workflow version
  are drafts. Release preparation resolves/requires every digest and rejects null or stale values.
- Policy resolution also returns the authoritative policy `kind`. Release requires exactly one
  resolved `market`, `broker`, `execution`, and `portfolio-risk` kind, with no missing/duplicate/extra
  kind; draft null-digest selections must still resolve through the policy registry so their kind is
  known before release.
- Every dependency contains exactly `path`, `role`, and optionally `pinned`; paths are unique, role
  is `normative` or `reference`, `pinned` is a boolean allowed only for reference dependencies, and
  normative dependency digests remain release-evidence output rather than caller metadata.
- `authoring_basis` contains exactly `mode` and `confirmed_decisions`. Mode is
  `repository-source`、`pasted-source`、`guided`, or `accepted-changes`; decisions are an ordered list
  of unique, non-empty UTF-8 strings. `repository-source` and `pasted-source` require `--source`;
  `guided` forbids it. Initial family creation forbids `accepted-changes`.
- `--source` is a regular non-symlink read-only input containing the exact pre-transformation source.
  For `repository-source` it must be inside the repository; for `pasted-source` it may be a temporary
  extracted input. The service, not caller JSON, computes and renders the persisted README
  `Authoring basis`: mode, repository-relative source path when applicable, current complete source
  commit when tracked, exact source SHA-256 when supplied, and confirmed decision summary. A tracked
  source with index/worktree drift records the exact worktree digest and does not falsely claim that
  the commit contains those bytes.
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
uv run pytest tests/test_workflow_authoring.py
uv run trading workflow validate --all
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: a complete new-family draft or proposed change is created without manual ID allocation,
template replacement, registry editing, index synchronization, or partial-state cleanup.

## Task 6: Add atomic next-version creation and in-place update

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/core/workflow_studies.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `tests/test_workflow_studies.py`
- Modify: `.agents/skills/trading-author-workflow/references/evolve.md`
- Modify: `.agents/skills/trading-author-workflow/references/impact.md`
- Modify: `.agents/skills/trading-operate-workflow/SKILL.md`
- Modify: `.agents/rules/workflow-study-governance.md`
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

**Replacement-boundary disposition contract:**

- Release preparation for `v002+` accepts
  `--dispositions <replacement-dispositions.json>` whenever the superseded active version has
  paused studies. Keys are exact old study paths; each value is an object containing exactly
  `action` and `target_version_path`.
- `action` is `continue`、`restart`, or `close-invalidated`. Continue/restart require
  `target_version_path` to equal the exact registered replacement draft path; close-invalidated
  requires null. No disposition claims a target study identity before that study is separately
  CLI-allocated under the released replacement.
- Every paused old study appears exactly once; completed/cancelled studies and unknown paths are
  forbidden. Release evidence stores the normalized ordered mapping as normative authorization. A
  later continue/restart
  creates a new study under the replacement and records the exact old `revisits` path through
  `trading-operate-workflow`; authoring never moves or resumes the old study.
- Initial release forbids the input. Replacement release with no paused studies accepts no file and
  records an empty mapping. The guarded release service validates this mapping under the shared
  Task 3 lock immediately before commit decision.
- `WorkflowStudyService.initialize()` enforces the mapping inside the common mutation-entry gate.
  A non-null `revisits` path is allowed only when an immutable release disposition targeting the
  exact active version authorizes `continue` or `restart`; `close-invalidated` is permanently
  ineligible. The service derives and records the authorized action in the new study metadata rather
  than accepting it from the caller.
- Each continue/restart authorization is single-use. Under the lock, initialization scans the target
  version's studies and rejects a second study with the same exact `revisits`; repository validation
  also detects duplicates, action/mapping mismatch, wrong target version, or a revisit from any
  close-invalidated ancestor. Cross-version continuity then proceeds through the newly created study
  path, not by repeatedly consuming the original mapping.
- Old source-version study bytes remain unchanged. After replacement they may remain historically
  `paused`, but release/retirement evidence governs whether a new study may revisit them; neither the
  version transition nor validator pretends the old study lifecycle itself became terminal.

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
- [ ] Add release parser/service/evidence tests for the typed replacement dispositions, exact target
  version path, one-to-one paused-study coverage, forbidden target study preallocation, and
  authoring-vs-study races under the shared lock.
- [ ] Add study-init and repository-validation tests proving exact-target continue/restart is
  single-use, close-invalidated cannot be revisited, missing/mismatched mapping fails, authorized
  action is service-derived, and historical paused bytes remain unchanged. Update the operate skill
  and shared governance reference to describe this enforced handoff without granting authoring
  permission to create the new study.
- [ ] Do not end or migrate old studies while creating a draft; version-boundary safety remains a
  release-time check because the active version is still authoritative.
- [ ] Publish replacement create/update, registry bytes, and generated indexes through the Task 3
  journal so exceptions and process restarts deterministically recover the selected before/after
  state.
- [ ] Add concurrent evolve/evolve and evolve/change tests proving version allocation、draft update
  and accepted-change refresh remain serialized without lost updates.
- [ ] Ensure abandoning a replacement draft does not recycle its version number.
- [ ] Run focused authoring tests and full workflow validation.

Expected: modifying a workflow requires one accepted change set and one complete replacement
contract, without manual version allocation, copying, registry edits, or source-change wiring.

## Task 7: Simplify abandon, retire, and deletion semantics

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/core/workflow_studies.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `tests/test_workflow_studies.py`
- Modify: `.agents/skills/trading-author-workflow/references/remove.md`
- Modify: `.agents/skills/trading-author-workflow/references/impact.md`
- Modify: `.agents/skills/trading-operate-workflow/SKILL.md`
- Modify: `.agents/rules/workflow-study-governance.md`
- Modify: `CLAUDE.md`
- Modify: `docs/ARCHITECTURE.md` if public entry-point documentation lists the new aliases

**CLI aliases:**

```bash
uv run trading workflow abandon <draft-version-path>
uv run trading workflow retire <active-version-path> \
  --dispositions <retirement-dispositions.json> \
  --reason <reason> --approved-by <human-id>

uv run trading workflow version transition <active-version-path> --to retired \
  --dispositions <retirement-dispositions.json> \
  --reason <reason> --approved-by <human-id>
```

The existing `workflow version transition` command remains available, but its retired branch now
requires exactly the same reason/disposition/approval inputs as the alias. Both parsers dispatch to
one evidence-producing repository method; there is no optional unsafe retirement path. The
`draft -> abandoned` branch rejects reason/disposition parameters. `abandon` is likewise only parser
sugar over that guarded branch.

**Retirement disposition contract:**

- `retirement-dispositions.json` is a closed input object whose keys are exact repository-relative
  paused-study paths under the active version and whose values are exactly `close-invalidated`.
  Pure retirement is terminal: it has no replacement target and therefore rejects continue/restart
  spellings or target version/study paths. Continue/restart must use the Task 6 replacement-release
  disposition contract instead.
- Every paused study must appear exactly once; completed/cancelled studies must not appear. Unknown,
  duplicate JSON key/path, absolute, symlinked, outside-version, or status-mismatched paths fail
  closed.
- Successful retirement creates immutable `RETIREMENT.json` under the retired version. It records
  schema version, workflow/version/path, exact release digest, current-time `retired_at`, stable
  `retired_by`, reason, and the ordered exact dispositions.
- The root registry version record stores the exact retirement-evidence SHA-256 beside the retired
  lifecycle state. This is an additive registry schema extension, not a registry-storage migration.
- `RETIREMENT.json` is add-only and digest-pinned. Retirement does not modify the released
  `WORKFLOW.md` or existing `RELEASE.json`; validation treats later retirement evidence as separate
  lifecycle evidence rather than a rewrite of release bytes.
- Retirement dispositions are normative close authorizations. Old studies remain historically
  paused, but `WorkflowStudyService.initialize()` and repository validation reject every future
  `revisits` chain that names a study closed by immutable retirement evidence.
- Retirement artifact, registry transition, indexes, and disposition validation publish through
  the Task 3 transaction coordinator.

- [ ] Add parser and dispatch tests for `abandon`、`retire`, and both branches of
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
- [ ] Prove `abandon` accepts only a registered draft and permanently retains its registry entry.
- [ ] Prove superseded, retired, abandoned, or released versions cannot be physically deleted by
  either command.
- [ ] Keep unregistered local-draft deletion outside the generic CLI. The skill must show the exact
  path and use the shared identity scanner to prove it is absent from every canonical current/
  historical path and textual reference. Non-Git、shallow、timeout/error or incomplete-history proof
  fails closed. The skill resolves current Git status, warns about recoverability, and obtains
  separate explicit confirmation before direct deletion. If it was ever tracked or referenced,
  refuse physical deletion and leave the path untouched; this plan does not invent an implicit
  tombstone/adoption mutation. If such a path is already missing, the Task 5/6 historical reservation
  scan still permanently blocks identity reuse and reports governance repair.
- [ ] Prove an ever-tracked/referenced unregistered path is refused without mutation, and that an
  already-missing historical identity still blocks create/evolve allocation. A future
  adopt-as-abandoned repair API is outside this simplification unless separately designed and
  approved.
- [ ] Ensure the skill reports whether the user's word “delete” was resolved to local deletion,
  abandon, retire, or refusal.

Expected: users can ask to remove a workflow without first knowing lifecycle vocabulary, while the
repository preserves every registered or released historical identity.

## Task 8: Full migration-free verification and handoff

**Files:**

- Verify all files changed in Tasks 1–7.
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
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-author-workflow
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-operate-workflow
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-evaluate-study
uv run pytest tests/test_workflow_authoring.py
uv run pytest tests/test_workflow_authoring_transaction.py
uv run pytest tests/test_workflow_identity.py
uv run pytest tests/test_workflow_studies.py
uv run pytest tests/test_study_qualification.py
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
     snapshot, then accept it; separately exercise explicit withdrawal;
  3. aggregate two accepted changes into one replacement draft;
  4. accept another change and update the same replacement draft identity in place;
  5. abandon a draft and prove registry、all canonical path/text references、Git history and
     concurrent allocation cannot reuse its number; prove non-Git、shallow and Git-error cases fail
     closed for vNNN/Cxxx/Sxxx;
  6. release a replacement with typed exact-target dispositions; prove study init consumes each
     continue/restart exactly once, derives the action, and rejects close/missing/wrong-target
     revisits;
  7. separately retire an active workflow through both alias and low-level command, prove byte-
     identical evidence, and reject the old no-reason/no-disposition bypass plus running/open/
     incomplete cases;
  8. race study init/resume/sync against release and retirement, proving the shared lock and in-lock
     precondition reread preserve the version boundary;
  9. crash at every transaction phase and immediately invoke every study writer, proving the common
     pending-journal gate recovers first or writes nothing; verify workflow-before-qualification lock
     ordering;
  10. inject external target changes before commit decision and between publications, proving CAS
      behavior, fresh-process rollback/roll-forward, status/recover, and fsync ordering;
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

Expected: the simplified authoring experience is additive, deterministic, migration-free, and
fully compatible with existing workflow history.

## Completion criteria

The plan is complete only when all of the following are true:

- A normal review does not load unrelated create/evolve/remove/release instructions.
- `trading-operate-workflow` and `trading-evaluate-study` load the canonical study-governance
  reference without depending on deleted/moved authoring-mode details.
- Existing and new authoring writes recover deterministically across exceptions, process restart,
  and the documented host/filesystem crash model under one durable journal; all study writers share
  the same mutation-entry gate, recover/reject pending journals first, follow workflow-before-
  qualification lock ordering, and re-read lifecycle preconditions inside the lock.
- Commit decision requires a full before-state CAS recheck; publication never overwrites a target
  whose kind/mode/digest moved outside the recorded before/after states.
- A complete new workflow can reach a validated v001 draft without manual ID allocation, template
  copying, registry editing, sync invocation, or partial cleanup.
- A new family is always `v001`; any same-slug registry/path/current-or-historical reference is a
  collision or governance-repair condition, never permission to create an initial `v002`.
- A new change uses exactly one `CHANGE.md` and retains the same proposal, impact, validation,
  decision, release, and audit semantics as the legacy representation.
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
  close-invalidated studies cannot be revisited, while their historical paused bytes remain intact.
- `retire` and `version transition --to retired` use one evidence-producing method; neither provides
  a reason/disposition bypass.
- Existing v001–v008 workflows, releases, studies, and legacy changes validate without migration.
- No registered or released workflow history is physically deleted.
- Never-used allocation includes registry、disk、inbound references、Git path history 與 concurrent
  reservations, including version-scoped canonical textual identities and exact references found
  only in Git historical content. Non-Git、shallow or Git-error proof fails closed for v/C/S IDs.
- Initial/replacement metadata has one closed schema, preserves service-verified authoring
  provenance, and defines capability/policy/dependency types, uniqueness, and draft null-digest
  behavior.
- New authoring rejects unknown capabilities, and release resolves exactly one market、broker、
  execution and portfolio-risk policy kind; legacy workflow bytes remain migration-free.
- Schema-v2 change metadata rejects unknown/stale decision state and preserves deferred/reproposal
  history through append-only, byte-replayable, digest-pinned decision snapshots.
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
  Shadow, activation, or trading authority. Tasks 3 and 6 only add the shared mutation gate,
  lock-order correction, and enforcement of version-boundary disposition authority; they do not
  alter frozen plans, evidence, outcomes, or existing study bytes.
- Releasing or retiring any actual repository workflow as part of the authoring-tool improvement.

## Recommended merge sequence

Keep each step independently reviewable and do not begin later happy-path CLI work until the prior
foundation is merged and green:

1. **PR 1 — Skill routing compatibility:** Tasks 1–2 only. Add progressive disclosure, retain the
   compatibility pointer, and update author/operate/evaluate callers.
2. **PR 2 — Transaction and identity foundation:** Task 3 only. Add the common pending-journal gate,
   workflow-before-qualification lock ordering, bounded WAL target operations, CAS rechecks, and
   fail-closed v/C/S identity proof; retrofit sync、transitions、release and study writers without
   adding schema-v2 or create/evolve commands yet.
3. **PR 3 — Change schema v2:** Task 4 only. Add normalized dual reader, direct index targets,
   append-only replayable decision snapshots, `change decide`, and explicit `change withdraw`; keep
   legacy assets until final caller verification. This PR does not expose `change create` yet.
4. **PR 4 — Draft authoring happy paths:** Tasks 5–6. Add `change create`, strict closed metadata and
   authoring provenance, supported-capability/four-policy validation, exact-v001/never-used
   allocation, replacement draft creation, machine-enforced single-use replacement dispositions,
   and in-place `--update`.
5. **PR 5 — Lifecycle UX and final migration-free verification:** Tasks 7–8. Add retirement
   evidence, safe low-level transition parity, abandon/retire aliases, documentation, forward tests,
   and remove obsolete writer assets only after inbound-link checks pass.
