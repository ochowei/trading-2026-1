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
unregistered local draft → 回報 exact path/Git status 並保持 untouched；實體刪除不在本計劃自動化
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
  新 create/evolve）、每個 `WorkflowStudyService` write，以及任何使用 workflow authority 的
  non-dry-run qualification registration（`register-study` 與 generic `register --workflow`）都必須
  使用同一 repository-scoped lock。所有 writer 取得
  lock 後必須先處理 pending authoring journal，並在任何 eligibility-changing write 前依固定順序
  recovery/reject 受影響 studies 的 qualification commit-decision journals，再重讀 lifecycle
  preconditions；任何 outcome-relevant writer 都不得繞過任一 crash recovery gate。Authoring
  mutation 另使用 durable transaction protocol。捕捉到的 exception、process crash、host/power
  loss或重新啟動後，不得留下不可判讀的 partial state。既有 study lifecycle states 與 outcome
  authority 不因此改變。
- `workflows/README.md` frontmatter 繼續作 lifecycle authority，不搬移 registry storage。Task 8
  在同一 PR 將 repository 的 root registry 由 schema 1 升為 schema 2；這是唯一 metadata schema
  migration，不重寫任何 version、release、change 或 study bytes。
- 不新增可任意刪除 workflow bytes 的 CLI；unregistered local draft 的實體刪除亦明確延後。
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
   authority；human decision 後只允許 writer 另建 content-addressed decision-event sidecars。新 event
   在 exact event 與對應 `CHANGE.md` bytes 進入 current `HEAD` 前是 `unanchored`，不得授權後續操作。
3. **No mixed representation.** 同一 change directory 同時出現 legacy 與 v2 authority 時，
   validation fail closed。
4. **Source-change paths remain directory paths.** Version metadata 與 release evidence 的
   `source_changes` 繼續指向 change directory，不因內部格式改變而破壞 lineage；schema-v2
   release 另保存每個 terminal `CHANGE.md` 與 decision-event manifest 的 digest；event 先由 exact
   current-`HEAD` tree anchor 建立不可改寫邊界，release 再 pin terminal authority manifest。
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
10. **Never-used allocation includes reachable history and concurrency.** Allocator 在同一
    repository lock 內掃描 registry、現存 paths、current inbound references、stage-0 index、
    untracked non-ignored files，以及所有已枚舉 locally reachable refs 的 Git path/blob history。
    在這個 proof universe 內出現過的 identity 不因目錄刪除而重用。
11. **Initial identity is always v001.** 新 family 只能建立 `v001`。若同 slug 的 `v001` 曾出現在
    registry、current filesystem/index/inbound references 或 enumerated reachable-ref path/blob
    history，CLI 視為 collision／governance repair，而不是建立 initial `v002`。
12. **Retirement is terminal in this plan.** 純 retirement 不建立 replacement version，也不接受
    continue/restart dispositions。未來若要復活 retired family，必須另立 lifecycle 設計。
13. **Dispositions are machine-enforced authorization.** Replacement/retirement dispositions 不只是
    文件敘述；study initialization 與 repository validation 必須執行 exact mapping、single-use 與
    close-invalidated 規則。
14. **Unknown capabilities fail closed for new authoring.** 新 draft/release 的 capability 必須存在於
    single canonical supported registry；legacy bytes 維持讀取相容。Draft 建立與 release 都驗證
    恰有 market、broker、execution 與 portfolio-risk 四種 resolved policy kinds。
15. **Never-used proof requires complete reachable-ref enumeration.** Allocation 在 non-Git、
    shallow clone、Git timeout/non-zero 或無法掃描所有 locally reachable refs 時 fail closed；
    deleted-branch/reflog-only、GC-pruned 或尚未 fetch 的 commits 明確不在證明範圍。若日後恢復的
    ref 含有可辨識的 divergent canonical allocation，validator 必須在下一次 mutation 前 fail
    closed；其他恢復 evidence 只擴大後續 proof universe，不宣稱能追溯 allocation 當時不可見的 ref。
16. **Release readers are dual-schema before v2 writes.** Task 7 在任何 schema-v2 release 可成為
    active 前，先讓 authoring、workflow-native execution、research CLI 與 qualification readers
    共用 closed-schema v1/v2 parser；schema v1 沒有 dispositions 只代表不能授權新的跨版本 revisit。
17. **Revisit actions have machine meaning.** Same-version source 必須是 terminal `cancelled` 或
    `completed`；`draft` 與其他 open states 均 fail closed。Cross-version `continue` 只可源自
    `paused` study，
    並要求新 study preregistration 時的 hypothesis bytes 與 source frozen hypothesis 完全一致；
    `restart` 亦只可源自 `paused`，但允許新 hypothesis/plan。兩者都建立新的 preregistration、
    evidence 與 outcome identity；`close-invalidated` 不可消耗。
18. **Authoring basis is audit provenance.** Draft 可在受控 update 中替換 authoring basis；release
    schema v2 必須複製 normalized basis 並 pin canonical JSON digest，之後不得漂移。
19. **Unregistered physical deletion is deferred.** Remove mode 可分類並回報 unregistered local
    draft，但不得刪除它；本計劃不新增 deletion-specific proof API、reservation ledger 或 direct
    filesystem deletion path。這不改變成功 import 後對「原始 source file」的獨立 disposition；
    source file 不是 workflow identity directory，仍依 create contract 精確確認處理。
20. **Schema-v2 rollout has no unsafe merge state.** Tasks 4–7 是同一不可分割 rollout。Task 4
    先讓 legacy release writer 對 schema-v2 source change fail closed；Tasks 5–6 建立的任何帶新
    authoring-basis contract 的 draft 亦不得走 schema-v1 release。只有 Task 7 的完整 v2 writer、
    readers、consumers 與 tests 同時就緒後才能合併／部署；中間 commit 不可發布欠缺 v2 evidence
    的 immutable release。
21. **Prepared is not effective release authority.** `workflow release` 只準備 worktree bytes。
    Outcome-relevant readers 必須證明 lifecycle/immutable-metadata projections 與所有 exact pinned
    files 等於 current HEAD，且 current HEAD
    等於 `refs/remotes/origin/HEAD` 所解析的本地 canonical tracking-ref tip；missing、unresolvable
    或 shallow proof fail closed。此 proof 不宣稱知道尚未 fetch 的 remote commit，操作文件要求先
    明確更新 tracking ref。這使 feature-branch commit、dirty preparation 與已知落後 checkout 都
    不能提前授權。
22. **Legacy cross-version revisits use one closed cutover manifest.** Task 7 生成一次性
    `workflows/LEGACY_REVISITS.json`，以 pre-Task-7 canonical commit 與 exact bytes/digests 列舉該
    commit 已存在的所有 cross-version edges。只有 manifest 中可由該 Git commit 重算的 edge 可
    grandfather；缺少 v2 fields 本身永遠不是 legacy 證明。
23. **Retired policy preserves existing exact pins, not new selection.** Exact workflow release pin
    可繼續解析其後被 retired 的 policy；新 draft/release selection 一律拒絕 retired status。
    Execution 與 authoring 使用分離的 explicit APIs，不以一個模糊 `resolve()` 同時代表兩種權限。
24. **Registry migration must be HEAD-anchored before another registry write.** Schema-2 migration
    產生的 exact marker 與 `after_sha256` registry blob 必須先同時出現在 current HEAD；在此之前
    所有後續 registry mutation fail without writes。Validator 往後固定第一個 anchored marker
    blob，並要求 HEAD ancestry 中存在該 exact pair。

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
- Identity、unregistered-local classification、retirement、release、authority and research-validity
  decisions remain individually confirmed; low-risk editorial decisions may be confirmed together.

- [ ] 先做 rule inventory：對每條現有說明標示 `keep`、`remove-generic`、`remove-duplicated`、
  `enforced-by-code` 或 `move-to-reference`。只保留會改變 Agent 決策的非顯而易見 invariants；
  不把整份舊 contract 機械拆成六份。
- [ ] 每條保留規則只存在於一個 canonical reference；`SKILL.md` 與 compatibility pointer 不
  重複 normative text。
- [ ] Routing tests允許 author impact與 study revisit情境共同載入 version-boundary reference，
  同時斷言它們不載入彼此無關的 authoring mode files。
- [ ] Preserve repository precedence, immutable released workflow behavior, source disposition,
  study scope separation, and release authority.
- [ ] Replace the old absolute “any committed identity” wording in the author skill/compatibility
  contract with the exact current/index/untracked-nonignored plus enumerated-reachable-ref guarantee;
  document deleted/ref-only/GC/unfetched exclusions and do not imply a durable reservation ledger.
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
- Modify: `src/trading/core/qualification_transaction.py`
- Modify: `tests/test_workflow_authoring.py`
- Create: `tests/test_workflow_studies.py`
- Create: `tests/test_qualification_transaction.py`
- Modify: `tests/test_study_qualification.py`
- Modify: `tests/test_qualification_workflow.py`
- Modify: `src/trading/cli.py`
- Modify: `.github/workflows/lint.yml`
- Modify: `CLAUDE.md`
- Modify: `.gitignore` only if the existing `state/` rule does not already cover the journal
- Modify: `docs/ARCHITECTURE.md`

**Lock and durability contract:**

- One repository-scoped filesystem lock serializes identity allocation、every authoring write、every
  `WorkflowStudyService` mutation that writes under `workflows/`, and non-dry-run workflow-derived
  qualification registration. The lock implementation supports an explicitly passed/re-entrant lease so a study
  mutation can call index sync or qualification code can take its inner lock without deadlocking or
  releasing the boundary midway.
- Every scoped writer uses one `enter_workflow_mutation()` invariant: acquire the shared lock;
  inspect the pending authoring journal; automatically execute the deterministic action already
  selected by a valid pristine `prepared`/`commit-decided`/`complete` phase; durably mark a prepared
  mismatch as `prepared-conflicted`; fail closed with phase-specific status/recover/abort guidance for
  corrupt、foreign or conflicted journals; then re-read registry, exact version, study inventory, and
  caller-specific lifecycle preconditions. Release/retire cannot rely on a safe-study check made before
  the lock; study init/resume cannot rely on an active-version check made before the lock.
- Before changing any study/version/consumption eligibility, the mutation entry derives impacted
  studies while holding the workflow lock: the exact study being changed; every study beneath a
  version being released/retired; and any revisit source consumed or referenced by initialization.
  From each frozen qualification spec it derives the authoritative qualification registry path,
  rejects missing/malformed identities, de-duplicates paths, and acquires their study-registration
  locks in sorted normalized repository-relative order. It then discovers and deterministically
  recovers any qualification transaction journal for those registries before re-reading workflow and
  study preconditions. A durable qualification journal is already commit-decided and has no rollback
  branch; lifecycle mutation may proceed only after its exact roll-forward and cleanup succeeds.
- Global lock ordering is `workflow repository lock -> sorted qualification study-registration
  locks -> qualification transaction journal lock -> trial-registry internal lock -> qualification-
  registry internal lock`. Study completion paths and non-dry-run
  `compile_study_qualification_plan()` must be refactored to acquire them in this order; no code path
  may hold an inner lock while waiting for an outer lock. Dry-run qualification compilation remains
  read-only and acquires neither writer lock.
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
  generic tree transaction API. Unregistered local-draft physical deletion is deferred, not another
  transaction operation.
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
     Any mismatch leaves canonical bytes untouched, durably changes the phase to
     `prepared-conflicted`, records exact conflict paths and detection time, fsyncs the journal parent,
     and reports the conflict;
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
  virtual proof tokens, staged paths, phase, and any conflict paths/time.
  `prepared` recovery never writes canonical targets and may discard staging/journal only when every
  target still matches recorded before-state **and** every assert-only read-set/virtual proof token
  still matches. Any mismatch durably becomes `prepared-conflicted` before returning. A
  `prepared-conflicted` journal never auto-cleans or returns to `prepared`, even if bytes later drift
  back; only the audited discard command below may remove it. `commit-decided` recovery rolls forward
  the exact after-state and cannot be aborted. `complete` recovery requires every target to match
  after-state, then performs cleanup only; missing staging is already-clean and does not fail. Any
  phase/state combination outside these rules fails closed with the exact conflicting path.
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
- `recover_impacted_qualification_transactions(impacted_study_paths, *, lease)`, which discovers
  frozen registry identities, takes sorted qualification locks and completes already-decided journals
  before eligibility changes.

**Operational CLI:**

```bash
uv run trading workflow authoring status
uv run trading workflow authoring recover
uv run trading workflow authoring abort-prepared <operation-id> \
  --reason <reason> --by <stable-operator-id>
```

`status` is read-only. `recover` requires the shared lock and only handles pristine `prepared`,
`commit-decided`, or `complete`; it never accepts replacement inputs、a caller-selected rollback
direction or a `prepared-conflicted` journal. Normal authoring and study writers automatically recover
those valid phases through the same mutation entry. `prepared-conflicted` has exactly one legal exit:
the audited `abort-prepared` path. It requires the exact operation
ID、stable actor and reason, is legal only while phase is `prepared` or `prepared-conflicted`, and
rechecks that no target was published and every target still matches its recorded before-state. The
read-set/proof token need not still match because the operation is being discarded. It never changes
canonical targets. Operation IDs are writer-generated canonical UUIDs, never caller-selected. Before
cleanup it atomically creates, with `replace=False`, one local-only record at
`state/workflow-authoring/aborts/<operation-id>.json`. The closed record has exactly
`schema_version`、`operation_id`、`journal_sha256`、`phase`、`target_manifest_sha256`、`conflicts`、
`aborted_at`、`aborted_by`, and `reason`; time is writer-generated and conflicts are the journal's
sorted exact paths. The file and parent are fsynced before journal/staging cleanup. Retry locates the
deterministic operation path even if the journal was already unlinked, requires the same journal
digest、actor and reason, preserves the original time,
and only finishes idempotent cleanup. A different retry fails closed. `commit-decided` cannot be
aborted; corrupt journals and `prepared-conflicted` journals are never auto-rewritten or auto-cleaned.

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
  check over the refs fetched into its non-shallow clone. Allocation does not claim knowledge of
  deleted-branch/reflog-only、GC-pruned or never-fetched commits. Restored refs join the next proof;
  validator rejects detectable divergent canonical allocations (for example independent add roots for
  the same canonical identity path), but does not claim retroactive knowledge of an unavailable ref.
  This plan does not add a durable identity ledger.
- Historical path and textual-content proofs are separate. Complete path history for the enumerated
  reachable refs comes from one
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
  parent-fsync boundaries; prove pristine prepared recovery cleans only when targets、read-set and
  virtual proof tokens all match, prepared-conflicted never auto-cleans, and complete recovery performs
  cleanup only.
- [ ] Add read-set tests covering dependency、policy release、study-precondition and evidence drift,
  plus target-before-state tests for source changes, before commit decision; each must write a durable
  `prepared-conflicted` marker without canonical mutation. Prove later byte reversion still cannot
  trigger auto-cleanup, while audited abort succeeds only when every target remains before-state.
  Drift after
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
  fresh repository process and prove deterministic recovery reaches exactly the before-/after-state
  selected by the journal phase, or remains durably `prepared-conflicted` without canonical writes.
  Verify file and parent-directory fsync ordering with a recording filesystem adapter rather than
  relying only on happy-path integration tests.
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
  add pending prepared/prepared-conflicted/commit-decided/complete journal tests and prove registration
  only proceeds after in-lock active/running/consumption validation.
- [ ] Characterize and retain the existing qualification journal as commit-decision WAL, then add
  fresh-process crashes after journal publication、trial-registry publication、qualification-registry
  publication and journal unlink. After each crash immediately invoke pause、cancel、awaiting-review、
  complete、release、retire and cross-version init as applicable; prove the outer workflow entry first
  takes sorted qualification locks, rolls the exact plan forward once, cleans the journal, re-reads
  eligibility, and only then performs or rejects the requested lifecycle write. Add two-registry tests
  proving deterministic path ordering and no workflow/qualification lock inversion.
- [ ] After a crash at every prepared/prepared-conflicted/commit-decided/publication phase,
  immediately invoke each study writer and prove it first completes the selected authoring recovery or
  fails without writing.
- [ ] Add reservation tests for all canonical path/text spellings, version-scoped local IDs,
  non-Git/shallow repositories, Git timeout/non-zero, missing objects, and `Sxxx` historical/inbound
  references; preserve permanent local scoping between unrelated workflow versions. Include the
  same blob OID at multiple historical paths、rename/delete history、stage-0-only reference、unmerged
  index、untracked-nonignored reference、ignored-file exclusion and ref/index/inventory CAS drift.
  Add cache hit/invalidation、blob de-duplication、token-boundary and deterministic timeout diagnostics.
- [ ] Add parser/dispatch tests for `workflow authoring status/recover/abort-prepared`, including clean
  state, fully pristine prepared cleanup, durable prepared-to-conflicted transition, no automatic
  conflicted cleanup after drift reversion, explicit audited prepared/conflicted abort with target
  precondition, commit-decided roll-forward, complete cleanup, corrupt journal refusal, and read-only
  status. Inject crashes before/after abort-record atomic publish、file fsync、parent fsync、journal
  unlink、each staging unlink and cleanup-parent fsync; prove same actor/reason retry preserves one
  original audit timestamp and only completes cleanup, while different retry inputs fail closed.
- [ ] Update `.github/workflows/lint.yml` to checkout with `fetch-depth: 0`, assert
  `git rev-parse --is-shallow-repository` is `false`, and run workflow authoring transaction、identity、
  study lifecycle、qualification transaction、study qualification and qualification workflow suites
  in addition to existing authoring/policy validation. CI must exercise the same fail-closed proof over
  refs fetched into the CI clone as local tests; it does not claim knowledge of never-fetched/deleted
  refs.
- [ ] Retrofit existing authoring mutations before adding new schema-v2 writers or happy-path CLI.
- [ ] Replace Task 1 characterization expectations with crash-safe assertions once the coordinator
  is active.
- [ ] Keep the journal local-only and free of credentials, broker exports, private ledgers, market
  outcomes, or other trading data.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring_transaction.py tests/test_workflow_identity.py \
  tests/test_workflow_authoring.py tests/test_workflow_studies.py \
  tests/test_qualification_transaction.py tests/test_study_qualification.py \
  tests/test_qualification_workflow.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: every existing authoring mutation is serialized and recoverable across exceptions、
process restarts and the documented filesystem crash model; study writers and non-dry-run
qualification registration share the same safe version boundary, and a qualification commit-decision
journal always rolls forward before an eligibility-changing workflow write, before new create/evolve
behavior is introduced.

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
- Each human decision/withdrawal transaction also creates one content-addressed canonical-JSON event at
  `decision-events/DNNN-<event-sha256>.json`. The event contains exactly `schema_version`、canonical
  change identity/path、sequence、status、recorded_at、recorded_by、the exact Validation/Decision input
  bytes or null where withdrawal permits it, their digests, and `snapshot_sha256`; `event_sha256`
  hashes the complete canonical event bytes and determines the filename. The event is a generated
  record, not a second authoring surface. Immediately after publication it is `unanchored`; neither
  stage-0 index presence nor another ref makes it authoritative.
- An event becomes `HEAD-anchored` only when `git ls-tree HEAD` proves the exact event path/blob and
  the current matching `CHANGE.md` blob are both present in the current `HEAD` tree. The tool never
  stages or commits automatically; after every decision/withdrawal it reports the pending Git anchor.
  Before deferred reproposal/decision、withdrawal、accepted-change create/evolve/release use, every
  prior event and the current pre-mutation `CHANGE.md` must match exact `HEAD` blobs. Otherwise the
  guarded operation fails without writes and reports that the records must first be reviewed and
  committed. Every schema-v2 mutation that changes `CHANGE.md` leaves the new current blob unanchored
  and reports the required commit; a later decision additionally produces a new unanchored event.
  Deferred reproposal therefore adds no event but still requires its new proposed `CHANGE.md` blob in
  current HEAD before another decision.
- Validator rejects filename/content digest mismatch、duplicate sequence, or modification/removal of
  a previously HEAD-anchored event. Before its first HEAD anchor, an event is not claimed immutable and
  cannot authorize downstream work; human/PR review plus the exact HEAD commit establishes the
  boundary. After anchoring, current-path/history validation rejects disappearance or rewrite, while
  schema-v2 release pins terminal `CHANGE.md` and every event. Non-Git、shallow、unmerged-index or
  incomplete reachable-ref proof fails closed for schema-v2 decision mutation/validation.
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
creates its content-addressed unanchored event and publishes lifecycle metadata/history in one
authoring transaction, then reports the required exact-HEAD anchor.
`change withdraw` does the equivalent for its withdrawal snapshot/event; it records an actor but is
not human approval of a research decision. The legacy low-level `change transition` remains
available for pre-authored legacy-format content.

For schema v2, low-level transition handles only `draft -> proposed` and `deferred -> proposed`.
Accepted/rejected/deferred decisions must use `change decide`; withdrawal must use
`change withdraw`. Callers can never pre-author or override history metadata or generated snapshots.
The transition reports that its new `CHANGE.md` blob needs a current-HEAD anchor before a decision;
the deferred branch also requires the prior event and pre-transition `CHANGE.md` to be anchored before
it writes. This restriction applies only to schema-v2 writes and does not rewrite legacy records.

`--validation` and `--decision` are substantive UTF-8 Markdown body fragments, not complete
documents. They must be regular non-symlink files, contain no YAML frontmatter, reserved four-section
heading, generated snapshot delimiter, or scaffold token, and resolve without path/symlink escape.
The same input boundary applies to `change decide` and `change withdraw`.

- [ ] Write failing tests for a valid v2 change, exact allowed frontmatter keys/types, every required
  section, and the complete section/metadata state matrix above, including first proposal,
  multiple deferred reproposals, terminal decision uniqueness, withdrawal after deferral, strict
  timestamp/sequence ordering, exact snapshot/event replay, tampered snapshot/digest/event rejection,
  historically HEAD-anchored event deletion/rename, and release. Prove stage-0-only or other-ref-only
  presence does not anchor an event; deferred reproposal/decision、withdrawal and accepted-change
  downstream use fail without writes until exact event plus current `CHANGE.md` bytes are in current
  HEAD. Prove reproposal changes only `CHANGE.md` but still requires that new blob to be committed before
  the next decision. After anchoring, include a test that tampers with `CHANGE.md` and recomputes every
  in-file digest but still fails against the anchored event/history contract.
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
- [ ] Update normalized release preflight so a draft may reference accepted source changes in either
  representation, but keep the schema-v1 writer fail closed whenever any source change is schema v2.
  It must not mark those changes released or mutate any bytes. The gate remains until Task 7 replaces
  it with the complete schema-v2 writer in the same rollout PR; add an explicit no-byte-change test.
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
writer-generated events whose authority begins at the documented HEAD anchor. They have equivalent
lifecycle、impact and decision semantics, while legacy release intentionally refuses them until the
atomic Tasks 4–7 rollout installs complete schema-v2 release evidence.

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
- Modify: `docs/policies.md`
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
  "policies": [
    {"family": "example-market", "version": "v001", "path": "policies/example-market--v001", "release_digest": null},
    {"family": "example-broker", "version": "v001", "path": "policies/example-broker--v001", "release_digest": null},
    {"family": "example-execution", "version": "v001", "path": "policies/example-execution--v001", "release_digest": null},
    {"family": "example-portfolio-risk", "version": "v001", "path": "policies/example-portfolio-risk--v001", "release_digest": null}
  ],
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
- Initial and replacement draft creation already requires exactly one authoritative `market`,
  `broker`, `execution`, and `portfolio-risk` kind, with no missing/duplicate/extra kind; the four
  hypothetical draft entries above illustrate the required cardinality. Draft null-digest selections
  must still inspect the policy registry so their kind is known before creation. Release rechecks the
  same four kinds and requires every exact digest.
- `PolicyResolver.inspect_registered(family, version)` is the single read-only authority for draft
  and released selection metadata. It validates registry status/path and closed policy config keys
  `schema_version`、`family`、`version`、`kind`、`values`, confirms identity/path agreement, and returns
  exact status/kind without treating a draft as executable. `resolve_for_new_selection()` accepts only
  active/superseded policies and is used by draft/release authoring; `resolve_exact_release_pin()`
  requires an exact `RELEASE.json` digest and permits active/superseded/retired status for execution of
  an already effective workflow release. Neither API accepts draft/abandoned policy execution, and
  workflow authoring must not add a second YAML parser or infer kind from family names. This split
  preserves existing immutable workflow pins when a policy is later retired without allowing new
  selection of retired policy.
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
  inspection、identity/path mismatch, exact retired-pin execution, rejection of retired new selection,
  and the boundary that `inspect_registered()` does not make a draft executable through either resolve
  API. Race policy retirement immediately before and after workflow authoring commit decision: the
  pre-decision case fails the selection CAS, while a post-decision exact pin remains executable.
- [ ] Move every capability constant、supported-set check and capability-to-behavior lookup into
  `workflow_capabilities.py`; update authoring、study service、qualification and CLI consumers in the
  same PR. Add an `rg`-based test/assertion that rejects hard-coded maintained capability literals
  outside the canonical module and explicit legacy fixtures.
- [ ] Keep workflow semantic completeness out of structural CLI tests. Add Agent/fixture review
  scenarios that check all 11 contract concerns even when headings are translated; CLI tests cover
  only machine-verifiable bytes/schema/identity rules.
- [ ] Make `create_initial_draft()` allocate exactly `v001`. Under the Task 3 lock, reject the slug
  if the shared fail-closed identity scanner finds that family/version in registry、current disk/index/
  inbound references or any enumerated reachable-ref path/blob; propagate non-Git/shallow/timeout/
  error proof failures and report collision/governance repair instead of
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
- [ ] Until Task 7 lands in the same rollout PR, make the legacy release writer reject every draft
  produced by `create_initial_draft()`/Task 6 evolve because it contains the new normalized
  authoring-basis contract. Prove the rejection changes no release、registry、change or index bytes;
  only the complete schema-v2 writer may lift this temporary gate.
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
  version-number reuse including enumerated reachable-ref historical-content references, metadata
  identity override,
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
- Modify: `src/trading/core/qualification_workflow.py`
- Modify: `src/trading/research_definitions/execution.py`
- Modify: `src/trading/cli.py`
- Create: `tests/test_workflow_release.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `tests/test_workflow_studies.py`
- Modify: `tests/test_study_qualification.py`
- Modify: `tests/test_qualification_workflow.py`
- Modify: `tests/test_qualification_cli.py`
- Modify: `tests/test_workflow_native_research_cli.py`
- Create: `workflows/LEGACY_REVISITS.json`
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
  VALIDATION/DECISION. Schema-v2 entries pin terminal `CHANGE.md` and every content-addressed
  decision-event
  sidecar. Missing/extra/reordered paths、event deletion or digest drift invalidate release evidence.
- `study_dispositions` is the normalized ordered array from the guarded input; each item contains
  exactly `source_study_path`、`action`, and `target_version_path`. Target path always equals the
  released replacement; it is retained even for close-invalidated so the boundary identity is
  explicit. The release SHA-256 makes the authorization immutable.
- Existing schema-v1 releases remain readable without migration. Absence of `study_dispositions` in
  schema v1 means “no new machine-consumable cross-version authorization.” It preserves a historical
  cross-version edge only through the closed `LEGACY_REVISITS.json` cutover proof below; field omission
  alone neither grandfathers nor authorizes anything.
- `workflow_release.py` owns the only closed-schema v1/v2 parser and normalized release model.
  Authoring validation、`WorkflowStudyService`、workflow-native execution、research CLI、study
  qualification and qualification workflow import it instead of checking schema numbers or keys
  independently. Execution resolves the same exact policy pins for v1 and v2; the shared parser
  rejects unknown governance fields before any consumer uses the release. The generic
  `qualification plan register --workflow` CLI removes its direct `json.loads(RELEASE.json)` path and
  obtains capabilities only from this normalized parser plus effective-authority check.

**Release authority phase:**

- Structural parsing distinguishes `prepared-unanchored` from `effective`; a valid worktree release is
  not automatically executable. `workflow release` may create prepared bytes on a branch and reports
  the exact Git/canonical anchor still required. It never stages、commits、fetches or moves refs.
- `require_effective_release()` resolves `refs/remotes/origin/HEAD` to a full canonical tracking ref,
  fails closed if Git/ref/object enumeration is missing、unresolvable、shallow or errors, and requires current
  `HEAD` to equal that ref's exact tip. It then requires the normalized root-registry lifecycle
  frontmatter projection and released-version immutable frontmatter projection to equal those parsed
  from HEAD, and requires exact worktree bytes for `RELEASE.json`、`WORKFLOW.md` and every release-pinned
  source/dependency/policy authority file to equal their HEAD blobs. Mutable generated index/errata
  prose and study paths are not release authority projections, so ordinary study sync does not revoke
  an effective release; they remain subject to normal repository/index validation. Symlink、index
  conflict or dirty authority drift fails closed. Unrelated dirty paths do not affect authority.
- Authoring validation may describe a structurally valid `prepared-unanchored` release so a PR can be
  reviewed, but every outcome-relevant consumer—study init/preregister/resume、cross-version
  consumption、workflow-native snapshot/run、both qualification CLI paths and qualification runtime—
  calls `require_effective_release()` and writes nothing unless it succeeds. Existing schema-v1
  releases use the same canonical-tip/HEAD gate without being rewritten.
- Tests cover dirty preparation、feature-branch commit、canonical tracking ref ahead/behind、missing
  `origin/HEAD`、missing object、frontmatter authority drift、exact pinned-file drift、ordinary generated
  study-index update and exact canonical-tip success. The
  proof explicitly does not infer unseen remote commits; documentation requires an explicit fetch/
  tracking-ref refresh before outcome work. A
  prepared release becomes effective only after the test repository merges it into its canonical ref
  and checks out/fetches that exact tip.

**Closed legacy cross-version boundary:**

- `workflows/LEGACY_REVISITS.json` has exactly `schema_version`, `cutover_commit`, and `entries`.
  Schema is integer 1; `cutover_commit` is the full pre-Task-7 canonical tip and must remain an ancestor
  of the current canonical ref. Each sorted entry has exactly `target_study_path`,
  `target_readme_sha256`, `target_preregistration_sha256`, `source_study_path`,
  `source_readme_sha256`, and `source_preregistration_sha256`.
- The Task 7 generator deterministically walks the complete Git tree at `cutover_commit` and emits
  every and only cross-version `revisits` edge present there. Validator independently replays that tree
  through Git object reads, recomputes both identities and exact digests, and rejects missing、extra、
  duplicate、reordered or caller-selected entries. The cutover commit must predate the manifest path,
  so adding an edge and then naming a newer feature commit cannot manufacture grandfathering.
- A manifest entry only preserves validation of that exact existing target/source byte pair; it never
  authorizes creating another study or consuming a disposition. Current files must still match the
  pinned identities/digests. Every post-cutover cross-version init requires schema-v2 release
  disposition and consumption regardless of whether fields are omitted manually.
- Once the manifest first enters HEAD, validator fixes its first-add blob through HEAD ancestry and
  rejects later modification/removal. Add fixtures for every real existing cross-version edge plus a
  hand-authored omitted-fields edge、changed source status/path/digest、newer cutover commit and edited
  manifest; only the exact deterministic baseline passes.

**Revisit branches:**

- Same-version revisit: when source and target study workflow-version paths are identical, source
  status must be terminal `cancelled` or `completed`. Draft redesign therefore uses the existing
  canonical sequence “cancel source, then create revisiting study”; `draft` and every other open state
  fail closed. No release disposition or consumption artifact is required; new metadata records null
  action/consumption.
- New direct cross-version initialization: when paths differ, the exact effective target release must
  authorize the exact source study with continue/restart. Close-invalidated、missing、wrong-target or
  schema-v1 absence fail closed. This branch never reclassifies already-existing manifest-pinned legacy
  edges as new authorization.
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
- Study initialization and every later source-study mutation re-read inbound `revisits` edges inside
  the shared workflow lock. Once referenced, a source must remain in the terminal state that made the
  edge legal; attempts to transition or mutate it fail before writes. Cancelling the revisiting study
  retains its directory and edge. There is no governed study-deletion path; manual disappearance of a
  registered/indexed revisiting study invalidates the repository and blocks every later mutation
  rather than freeing the source lineage.

**Study metadata and durable consumption:**

- After Task 7, every newly written study README includes `revisit_action`、
  `disposition_consumption`, and `disposition_consumption_sha256`, each null for no/same-version
  revisit. For an authorized cross-version revisit they equal the release action、exact consumption
  artifact path and its 64-hex digest. Studies pinned to a schema-v2 workflow release must contain
  all three keys. Studies already pinned to schema-v1 releases may omit all three as legacy-compatible
  bytes; the post-Task-7 writer still emits null fields for new same-version studies under those
  releases and never rewrites old studies. Omission is accepted only when the exact study README/path
  already exists at the legacy cutover commit with matching bytes; a post-cutover path cannot simulate
  legacy merely by omitting keys.
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
  authority manifest and immutable release authorization digest. Prove the legacy writer refuses
  schema-v2 changes/new authoring-basis drafts without changing bytes, while the final writer always
  emits schema v2; no intermediate rollout state can publish incomplete immutable evidence.
- [ ] Add canonical authority-phase tests for every consumer named above. Structural validation may
  inspect prepared-unanchored bytes, but study/research/qualification operations must fail without
  writes until exact authority projections/pinned files match HEAD and HEAD equals the refreshed local
  canonical tracking ref. Prove a normal study-index sync does not revoke authority but stale/invalid
  generated indexes still fail their ordinary validator. Preserve the explicit no-knowledge-of-
  unfetched-remote limitation in docs and diagnostics.
- [ ] Generate and test the deterministic legacy revisit cutover manifest against the exact pre-Task-7
  canonical commit. Cover every current cross-version edge, especially non-paused historical sources,
  and prove a new omitted-fields edge cannot enter the manifest or bypass disposition consumption.
- [ ] Add one real schema-v2 release fixture that passes `resolve_workflow_policy_set()`、workflow-
  native research CLI context construction and structured study/qualification runtime-contract
  checks. Prove v1 and v2 resolve identical policy sets and unknown/malformed v2 fields fail in every
  consumer through the shared parser. After pinning it, retire one selected policy and prove exact-pin
  execution remains valid while authoring a new draft/release with that retired policy is rejected.
- [ ] Extend the canonical CI focused command with `tests/test_workflow_release.py` and
  `tests/test_workflow_native_research_cli.py` plus `tests/test_qualification_cli.py`; the atomic
  Tasks 4–7 rollout must be green with real v1/v2 effective-release reader paths and the generic
  `qualification plan register --workflow` path, not rely on the later full-suite handoff.
- [ ] Add same-version、direct cross-version and cross-then-same-version revisit tests, plus missing/
  close/wrong-target authorization、graph cycle and cross-family rejection. Cover allowed same-version
  cancelled/completed sources、rejection of `draft` and every other open source with no changed bytes,
  explicit cancel-then-create success, and mechanical continue hypothesis equality versus restart
  freedom. Update the existing draft-source fixture to cancel the source before revisit.
- [ ] Add in-lock inbound-edge guard tests for every source mutation path. Prove manual/corrupt source
  drift fails validation, mutation fails before writes, cancellation retains the edge, and unsupported
  manual disappearance of a revisiting study invalidates the repository rather than freeing the source
  lineage.
- [ ] Add atomic consumption tests for pre-decision rollback、commit-decided recovery、single-use,
  cancellation permanence、deleted-study invalidity and concurrent double-init.
- [ ] Update only the canonical version-boundary reference with these rules; impact/study governance
  references route to it without restating schemas or lifecycle logic.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_release.py tests/test_workflow_authoring.py \
  tests/test_workflow_studies.py \
  tests/test_study_qualification.py tests/test_qualification_workflow.py \
  tests/test_qualification_cli.py tests/test_workflow_authoring_transaction.py \
  tests/test_workflow_native_research_cli.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: version-boundary dispositions become durable, auditable, single-use machine authority;
same-version redesign follows cancel-then-create or a completed follow-up, with inbound edges guarded
under the same lock and no old study bytes rewritten. Existing cross-version edges survive only through
the deterministic legacy cutover manifest, and no prepared release authorizes outcome work before its
exact local canonical-tip anchor.

## Task 8: Simplify abandon, retire, and deletion semantics

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/core/workflow_studies.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `tests/test_workflow_studies.py`
- Modify: `tests/test_qualification_transaction.py`
- Modify: `tests/test_study_qualification.py`
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
schema-1 retired entry because this repository has no approved grandfathered omission. The command
reports `pending HEAD anchor` and every subsequent root-registry mutation refuses to write until the
exact marker blob and registry blob named by `after_sha256` coexist in current HEAD.

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
  Before another registry mutation, `git ls-tree HEAD` must show the exact marker and exact
  `after_sha256` registry blobs together. After that first anchored pair, validator walks HEAD ancestry
  to fix the marker's first-add blob, requires an ancestor commit containing the pair, and rejects any
  current/history deletion、rewrite、replacement marker or root-registry downgrade. The historical
  pair remains replayable even though later legitimate registry mutations change current README bytes.
  No ordinary CLI can add a grandfathered record or expand an allowlist.
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
  input. Prove migrate followed immediately by abandon/release/retire/sync fails without writes until
  the exact marker/after-registry pair enters HEAD; after the anchor, retirement succeeds and later
  registry bytes may evolve while the ancestor pair stays replayable. Reject marker-first-add rewrite
  and a marker whose digest points to registry bytes that never coexisted with it in one commit.
- [ ] Prove `abandon` accepts only a registered draft and permanently retains its registry entry.
- [ ] Prove superseded, retired, abandoned, or released versions cannot be physically deleted by
  either command.
- [ ] Keep unregistered local-draft physical deletion outside both the generic CLI and skill
  automation. The skill reports its exact path and current Git status, labels it
  `unregistered-local/manual-work-outside-plan`, and leaves it untouched; it does not attempt the
  logically impossible proof that a present target is absent from the current path universe, nor add
  a deletion-specific public proof API、reservation ledger、implicit tombstone/adoption mutation or
  direct filesystem removal path.
- [ ] Prove remove mode leaves an unregistered local path byte-identical and emits the bounded manual-
  work classification. Separately prove an already-missing identity found within Task 3's stated
  current/reachable-ref proof universe blocks create/evolve allocation; a future deletion or
  adopt-as-abandoned repair API requires separate design and approval.
- [ ] Ensure the skill reports whether the user's word “delete” was resolved to unregistered-local
  manual work、abandon、retire, or refusal.
- [ ] Run:

```bash
uv run pytest tests/test_workflow_authoring.py tests/test_workflow_studies.py \
  tests/test_qualification_transaction.py tests/test_study_qualification.py \
  tests/test_qualification_workflow.py tests/test_workflow_authoring_transaction.py
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
```

Expected: users can ask to remove a workflow without first knowing lifecycle vocabulary; governed
states map to abandon/retire/refusal, and an unregistered local draft is reported but not mutated.

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
uv run pytest tests/test_qualification_transaction.py
uv run pytest tests/test_study_qualification.py
uv run pytest tests/test_qualification_workflow.py
uv run pytest tests/test_qualification_cli.py
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
     snapshot/event, require exact event plus current `CHANGE.md` in current HEAD before each guarded
     follow-up, then accept it; separately exercise explicit withdrawal, prove stage-0/other-ref-only
     records do not authorize use, and prove rewriting anchored authority cannot bypass the contract;
  3. aggregate two accepted changes into one replacement draft;
  4. accept another change and update the same replacement draft identity in place;
  5. abandon a draft and prove registry、all canonical path/text references、Git path/blob history over
     every enumerated locally reachable ref、stage-0 index and concurrent allocation cannot reuse its
     number; prove restored refs with divergent canonical allocation roots fail closed before mutation,
     and prove shared-blob
     multiple paths、unmerged index、non-Git、shallow and Git-error cases fail closed for v/C/S;
  6. allow same-version revisit only from cancelled/completed sources, prove draft and every other open
     source fail without writes, and guard referenced sources on every later mutation; then release a
     schema-v2 replacement with typed exact-target dispositions; prove it is structurally prepared but
     no outcome consumer can use it on a dirty worktree or feature-branch commit. Merge/check out the
     exact local canonical tip, then prove workflow-native execution/qualification can read it and
     atomically consume each cross-version continue/restart exactly once. Enforce their different
     hypothesis rules, preserve consumption after cancellation/deletion, and reject close/missing/
     wrong-target/cyclic revisits;
  7. generate the deterministic legacy cross-version manifest from a pre-rollout canonical commit,
     validate every existing edge including non-paused sources, and prove new omitted fields、changed
     cutover commit、extra entry or hand-authored edge cannot obtain grandfather status;
  8. atomically migrate the root registry to schema 2 and prove immediate retire/abandon/release/sync
     writes nothing. Commit the exact marker/after-registry pair to HEAD, then separately retire an
     active workflow through both alias and low-level command; prove byte-identical evidence and reject
     schema downgrade、marker rewrite/removal、unreplayable pair、the old bypass and open/incomplete cases;
  9. race study init/resume/sync and non-dry-run qualification registration against release、
     retirement and completion, proving the shared lock and in-lock precondition reread preserve the
     version boundary;
  10. crash both authoring and qualification journals at every commit/publication phase and immediately
      invoke every eligibility-changing workflow writer; prove the common gate rolls already-decided
      qualification work forward first or writes nothing, including sorted multi-registry locking;
  11. inject external target and validation-read-set changes before commit decision and between
      publications, proving durable `prepared-conflicted` marking、no auto-cleanup after byte reversion、
      audited abort preconditions、commit-decided roll-forward、complete cleanup、fresh-process status/
      recover and fsync ordering. Crash every abort-record/cleanup boundary and prove idempotent same-
      reason retry; prove post-decision non-target drift reports invalidity without retaining a
      completed journal;
  12. at the end of each logical Tasks 4–7 stage, invoke the public release CLI and prove schema-v2
      source/new-basis drafts cannot produce schema-v1 evidence; only the complete atomic rollout emits
      v2. Exercise both generic qualification CLI entry points through the shared parser;
  13. pin a policy, retire it, and prove the effective old workflow still resolves exact bytes while
      every new draft/release selection rejects the retired policy; race retirement around workflow
      commit decision;
  14. validate a mixed repository containing legacy and schema-v2 changes;
  15. verify legacy index links and schema-v2 direct `CHANGE.md` links.
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
  and the documented host/filesystem crash model under their defined journals; all eligibility-
  changing study/workflow writers share the same mutation-entry gate, recover/reject the authoring
  journal and impacted qualification commit-decision journals first, follow the complete sorted lock
  ordering, and re-read lifecycle preconditions inside the locks.
- Non-dry-run qualification registration uses the same workflow-before-qualification gate and can
  proceed only for an active running study with valid version-boundary consumption where applicable.
- Commit decision requires a full before-state CAS recheck; publication never overwrites a target
  whose kind/mode/digest moved outside the recorded before/after states.
- WAL records and CAS-checks every assert-only validation input that determines after-state.
  Post-decision non-target drift may fail repository health validation but cannot permanently retain
  an otherwise complete journal.
- Prepared recovery never writes canonical targets and cleans only if targets/read-set/proof tokens
  remain pristine; any mismatch durably becomes `prepared-conflicted` and never auto-cleans.
  Commit-decided recovery only rolls forward, complete recovery only cleans up, and explicit audited
  abort is limited to prepared/prepared-conflicted operations whose targets all remain before-state.
  A deterministic atomic abort record is fsynced before cleanup; same-input crash retry preserves one
  audit timestamp, while different retry inputs fail closed. `prepared-conflicted` never routes to
  `recover`.
- A complete new workflow can reach a validated v001 draft without manual ID allocation, template
  copying, registry editing, sync invocation, or partial cleanup.
- A new family is always `v001`; any same-slug reference in registry、current paths or the enumerated
  reachable-ref proof universe is a collision or governance-repair condition, never permission to
  create an initial `v002`.
- A new change uses exactly one author-edited `CHANGE.md`; only guarded decisions add generated,
  content-addressed event sidecars. A new event is unanchored and cannot authorize follow-up until its
  exact event plus matching current `CHANGE.md` bytes are in current HEAD; the tool never stages or
  commits automatically. It retains proposal、impact、validation、decision and release semantics.
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
  cancel/recreate and completed follow-up revisits remain valid without a release disposition;
  `draft` and every other open same-version source are rejected, and inbound edges guard all later
  source mutations inside the lock.
- Existing schema-v1 cross-version edges validate only through the deterministic pre-cutover Git
  manifest; missing new fields alone cannot grandfather a new edge.
- `retire` and `version transition --to retired` use one evidence-producing method; neither provides
  a reason/disposition bypass.
- Root registry schema 2 and its add-only migration marker make every new retired state require an
  exact retirement-evidence digest; schema downgrade or a newly omitted digest fails closed. No
  second registry mutation occurs until exact marker/after-registry bytes coexist in HEAD, and that
  first anchored pair remains replayable from HEAD ancestry.
- Existing v001–v008 workflows, releases, studies, and legacy changes validate without migration.
- No registered or released workflow history is physically deleted.
- Never-used allocation includes registry、disk、inbound references、complete path history and
  de-duplicated blob content over every enumerated locally reachable ref、stage-0 index、untracked
  non-ignored files and concurrent reservations. Grammar preserves per-version scoping; path proof
  never relies on the optional path attached to a de-duplicated blob, and ref/index/inventory proof
  tokens are CAS-checked before commit. Non-Git、shallow、unmerged-index、timeout or Git-error proof
  fails closed for v/C/S IDs. Deleted-branch/reflog-only、GC-pruned and never-fetched commits are outside
  the proof; restored refs join future proof, and detectable divergent canonical allocations block the
  next mutation without implying retroactive knowledge of previously unavailable refs.
- Initial/replacement metadata has one closed schema, preserves service-verified authoring
  provenance, and defines capability/policy/dependency types, uniqueness, and draft null-digest
  behavior. Draft creation itself requires exactly one market、broker、execution and portfolio-risk
  policy kind.
- New authoring rejects unknown capabilities and retired policy selections. Existing effective
  workflow releases continue resolving a subsequently retired policy only through its exact pinned
  release digest; selection and execution use distinct authoritative resolver APIs.
- Schema-v2 change metadata rejects unknown/stale decision state and preserves deferred/reproposal
  history through byte-replayable snapshots and content-addressed events; every guarded follow-up
  requires exact current-HEAD anchoring, and schema-v2 release pins the complete terminal
  source-change authority manifest.
- Schema-v2 release is accepted by the same closed dual-schema parser in authoring、workflow-native
  execution、research CLI and both qualification CLI/runtime consumers, and pins normalized authoring
  provenance. Tasks 4–7 have no merge/deploy point at which schema-v2 content can be released through
  schema-v1 evidence.
- A prepared worktree release never authorizes outcome work. Effective authority requires exact
  lifecycle/immutable-metadata projections plus pinned worktree/HEAD files and
  `HEAD == refs/remotes/origin/HEAD` local tracking-ref tip after an explicit refresh; the proof is fail
  closed for missing/unresolvable local Git evidence and does not claim knowledge of unfetched remote
  commits. Generated study-index updates are validated normally but are not mistaken for release drift.
- All focused tests, full tests, Ruff, skill validation, workflow validation, and diff checks pass.

## Explicitly deferred work

- Moving the root registry out of `workflows/README.md` frontmatter.
- Removing legacy five-file change parsing.
- Rewriting existing changes into schema v2.
- Removing existing low-level transition/sync commands.
- Adding a generic destructive `workflow remove` CLI.
- Automating physical deletion of an unregistered local draft, including any deletion-specific proof
  API, reservation ledger, tombstone/adoption flow or direct filesystem removal path.
- Adding a lifecycle that revives a retired workflow family.
- Adding an adopt/register-tombstone repair API for unregistered historical drafts.
- Changing unrelated study lifecycle states, approvals, evaluation, completion, qualification,
  Shadow, activation, or trading authority. Tasks 3 and 7 only add the shared mutation gate,
  cross-journal recovery ordering、effective-release/cutover checks and enforcement of version-boundary
  disposition authority; they do not alter frozen plans, evidence, outcomes, or existing study bytes.
- Releasing or retiring any actual repository workflow as part of the authoring-tool improvement.

## Recommended merge sequence

Keep foundations independently reviewable, but do not create a merge/deploy boundary inside the
schema-v2 writer/reader rollout. Tasks 4–7 may use reviewable commits on one branch; their temporary
release refusal guards stay active until the final commit and the whole PR is green:

1. **PR 1 — Skill routing compatibility:** Tasks 1–2 only. Add progressive disclosure, retain the
   compatibility pointer, and update author/operate/evaluate callers.
2. **PR 2 — Transaction and identity foundation:** Task 3 only. Add the common pending-journal gate,
   dual authoring/qualification WAL recovery ordering、bounded target/read-set CAS、crash-safe abort
   audit、explicit prepared-conflicted handling, and cached v/C/S proof over enumerated reachable refs;
   retrofit all eligibility-changing writers before adding schema-v2 or create/evolve commands.
3. **PR 3 — Atomic schema-v2 authoring and release rollout:** Tasks 4–7 together. In ordered commits,
   add normalized change reading/events and immediately block legacy release for v2 content; add
   change/create/evolve with four-policy/provenance rules while retaining that block; then add the
   closed legacy-revisit cutover、dual release parser/writer、canonical effective-release gate、all
   consumers、source/provenance pins and disposition consumption. Do not merge/deploy any intermediate
   commit. Final tests prove no public release invocation at any stage can create schema-v1 evidence
   for new-schema content.
4. **PR 4 — Lifecycle UX and history-compatible verification:** Tasks 8–9. First commit the atomic
   root-registry schema-2 migration and exact marker/after-registry pair; only a later commit may add
   retirement evidence and aliases. Add safe low-level transition parity、documentation and forward
   tests, then remove obsolete writer assets only after inbound-link checks pass.
