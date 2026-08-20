# Trading Workflow Authoring Simplification MVP

**Goal:** 讓 Agent 與人類以 intent、preview、approval 三個層次建立或演進 repository
workflow，不再手動配置 identity、複製 template、更新 registry/index 或組合低階命令；同時保留
released workflow immutability、human authority、study safety、exact policy/dependency pins 與既有
歷史格式相容性。

**Status:** Approved implementation plan. No implementation task is complete until its checkbox and
verification evidence are updated in the implementing change.

## Outcome

MVP 只增加高階 authoring façade 與必要的局部寫入保護。它沿用現有 repository formats、validators
與 lifecycle writers，不把作者體驗改善擴張成 storage/governance platform rewrite。

使用者完成一次 authoring 操作時只需要：

```text
描述意圖或提供來源
→ Agent 顯示完整 preview 與真正未決事項
→ 人類確認必要決策
→ CLI 配置 identity、建立既有格式、同步 indexes、驗證
→ 另行取得 change decision 或 release approval
```

MVP 完成後，以下行為成立：

- 新 workflow family 可由一份 confirmed request 建立 `v001` draft。
- active workflow 可由一份 confirmed request 建立下一個既有五檔格式的 change record。
- accepted changes 可建立或更新唯一 next-version draft。
- 每個 mutation 都先 preview；dry-run 不寫檔。
- identity、paths、registry 與 generated indexes 由 CLI 管理。
- 失敗的 preflight、validation 或 target-drift check 不留下 mutation。
- 發布仍需獨立 human approval；prepared release 仍只在 canonical branch 生效。

## Non-goals

本 MVP 不做以下工作：

- 不建立 `CHANGE.md` schema v2，也不增加 dual-schema release reader/writer。
- 不遷移 root workflow registry schema。
- 不建立跨 workflow/study/qualification subsystem 的 durable WAL 或 lock hierarchy。
- 不新增 persisted revisit disposition、consumption artifact 或 legacy cutover manifest。
- 不改變 retirement evidence、study lifecycle、qualification、Shadow、activation 或 trading
  authority。
- 不掃描所有 reachable Git blob/ref 來宣稱永久 identity proof。
- 不重寫或搬移任何既有 released workflow、change record、study 或 release evidence。
- 不自動刪除 workflow identity directory。
- 不編輯 `pm/`。

這些項目若仍有需求，必須各自提出獨立設計與風險理由，不得重新塞回本 MVP。

## Invariants that remain mandatory

1. `workflows/README.md` schema 1 frontmatter 仍是 lifecycle authority。
2. Legacy `README.md + PROPOSAL.md + IMPACT.md + VALIDATION.md + DECISION.md` change format 維持唯一
   read/write format。
3. Released `WORKFLOW.md`、`RELEASE.json` 與 pinned normative bytes 不得修改。
4. 新 family 固定從 `v001` 開始；replacement version 必須 trace 到 accepted source changes。
5. 不重用目前 registry、tracked paths 或 repository references 中已存在的 `vNNN`、`Cxxx`。
   Registered/referenced identities 不得刪除；unregistered 且從未 committed/referenced 的 local
   draft 不宣稱具有永久 reservation。
6. Release 前仍需 exact released market、broker、execution 與 portfolio policy pins、normative
   dependency digests、完整 contract、human approval 與 safe unfinished-study boundary。
7. Active version 被 supersede 或 retired 前，unfinished studies 仍須是 `paused`、`completed` 或
   `cancelled`；既有 impact/disposition 規則維持人工審查事項，本 MVP 不新增 consumption state
   machine。
8. CLI 驗證 structure、metadata、indexes、hashes 與 references；Agent 審查 semantic fidelity 與
   impact；human 才能授權 decision、release 與 retirement。
9. Authoring 不執行 study、不判斷 outcome，也不取得 broker/order/live authority。

## User-facing commands

新增三個 additive happy-path commands；既有低階 `sync`、`change transition`、`version transition`
與 `release` 保留供相容與診斷使用。

```bash
# 建立 initial v001 draft
uv run trading workflow create --request authoring-request.json --dry-run
uv run trading workflow create --request authoring-request.json

# 在 unique active version 下建立下一個 change record
uv run trading workflow change create --request change-request.json --dry-run
uv run trading workflow change create --request change-request.json

# 從 accepted changes 建立或更新唯一 next-version draft
uv run trading workflow evolve --request evolve-request.json --dry-run
uv run trading workflow evolve --request evolve-request.json
```

Request files 是操作輸入，不是 tracked authority。它們使用 closed JSON schemas，不能提供
allocated `vNNN`、`Cxxx`、current-time evidence、lifecycle status 或 approval timestamps。CLI 回傳
deterministic preview，列出：

- resolved mode、slug、source/active version；
- allocated identity 與 exact paths；
- source changes、policies、dependencies 與 authoring basis；
- registry/index/file changes；
- warnings、blocking issues 與 remaining human decisions。

Agent 只在 shared understanding confirmed 後執行 non-dry-run。Release、change decision、retirement、
source deletion 與 research-validity decisions 仍需個別授權。

## Minimal implementation architecture

### Progressive-disclosure skill

`.agents/skills/trading-author-workflow/SKILL.md` 只保留 routing、precedence、authority、mutation
pause point 與 finish report。Rules 依 mode 分到：

- `references/core.md`
- `references/create.md`
- `references/evolve.md`
- `references/remove.md`
- `references/release.md`
- `references/impact.md`

`references/workflow-authoring-contract.md` 變成 compatibility pointer，不複製 normative content。
Study-only lifecycle rules移到 shared canonical reference，讓 operate/evaluate skills 不需載入 authoring
create/evolve/remove 規則。

### High-level façade over existing formats

`WorkflowRepository` 新增 pure planning methods 與 applying methods：

```python
plan_create(request: CreateWorkflowRequest) -> WorkflowMutationPlan
plan_change(request: CreateChangeRequest) -> WorkflowMutationPlan
plan_evolve(request: EvolveWorkflowRequest) -> WorkflowMutationPlan
apply(plan: WorkflowMutationPlan) -> WorkflowMutationResult
```

Planner 只讀 repository，解析 current registry、active/draft version、existing changes、policies、
dependencies 與 exact target bytes。它產生完整 before/after manifest，不直接寫檔。

Writer 只使用現有 templates、schema 1 registry、legacy change format、`sync()` 與 `validate_all()`。
不新增第二套 lifecycle parser、release schema 或 authoritative representation。

### Bounded authoring mutation guard

MVP 使用一個 authoring-scoped repository lock，涵蓋新 high-level commands 與現有 authoring
`sync`、change/version transitions、release preparation。它不接管 study 或 qualification locks。

Apply sequence 固定為：

1. 取得 authoring lock。
2. 重讀 registry 與 target files，確認與 preview 的 exact digests 相同。
3. 在 repository-local temporary staging directory 建立完整 after tree。
4. 對 staged workflow root 執行相同結構與 generated-index validation。
5. 再次確認 canonical targets 未漂移。
6. 以 per-file atomic replace 發布，保留本次 before bytes 供同 process rollback。
7. 執行 canonical `validate_all()`；失敗時回復本次 before bytes 並再次驗證。
8. 清理 staging 並釋放 lock。

Process crash 可能留下未驗證的 partial worktree，但不會創造 canonical authority：draft/change writes
本身無 authority，prepared release 仍需進入 canonical branch。任何後續 authoring mutation 必須先跑
`validate_all()`，發現 partial state 即 fail closed 並要求人工檢查。本 MVP 不建立 durable journal、
prepared-conflicted state、abort audit 或跨 subsystem recovery。

### Identity allocation

- Version identity 由永久保留的 root registry entries 與 present version paths 配置。
- Change identity 由 active version 下保留的 change directories、current tracked index 與 current
  repository references 配置。
- Validator 拒絕 registered/referenced identity 消失或碰撞。
- 不讀取任意 blob contents、不對所有 ref tips 建立 CAS，也不因 shallow clone 本身阻止普通
  authoring；release 的既有 canonical-branch authority rule不變。

## Work package 1: Compatibility baseline and progressive disclosure

**Primary files**

- Modify: `.agents/skills/trading-author-workflow/SKILL.md`
- Replace: `.agents/skills/trading-author-workflow/references/workflow-authoring-contract.md`
- Create: `.agents/skills/trading-author-workflow/references/{core,create,evolve,remove,release,impact}.md`
- Create: `.agents/rules/workflow-study-governance.md`
- Modify: `.agents/skills/trading-operate-workflow/SKILL.md`
- Modify: `.agents/skills/trading-evaluate-study/SKILL.md`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `docs/ARCHITECTURE.md`

- [ ] 固定 legacy five-file change、schema 1 registry、release invariants 與 v001-v008 validation
  regression。
- [ ] 對舊 skill rules 作 inventory，只保留會改變 Agent 決策的規則；不機械複製整份 contract。
- [ ] 實作 mode-specific routing，普通 review/create/evolve 不載入無關 reference。
- [ ] 保留 repository precedence、released immutability、study scope separation、source disposition
  與 release authority。
- [ ] 更新 operate/evaluate skill 只讀 shared study governance。
- [ ] 驗證 skill package 與 maintained inbound links。

**Verification**

```bash
uv run pytest tests/test_workflow_authoring.py
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-author-workflow
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-operate-workflow
uv run --no-sync python /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/trading-evaluate-study
rg -n 'workflow-authoring-contract\.md' .agents/skills
```

## Work package 2: High-level create/change/evolve façade

**Primary files**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `.agents/skills/trading-author-workflow/assets/`
- Modify: `CLAUDE.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] 定義 closed request dataclasses/parsers 與 deterministic `WorkflowMutationPlan`。
- [ ] 實作 `plan_create()`：檢查 slug collision、固定 `v001`、解析四類 policy pins、建立既有
  workflow-version template、registry entry 與 indexes。
- [ ] 實作 `plan_change()`：解析 unique active version、自動配置下一個 `Cxxx`、建立完整 legacy
  five-file change record；預設保持 `draft`，只有完整 confirmed request 可選擇建立後立即走既有
  `draft -> proposed` transition。
- [ ] 實作 `plan_evolve()`：只接受 accepted changes；若已有唯一 registered draft 則原地更新，否則
  配置下一個未使用 version；所有 substantive rules 必須 trace 到 source changes。
- [ ] `--dry-run` 顯示完整 deterministic preview 且 zero mutation。
- [ ] Non-dry-run apply 完成 registry/index/file writes 後執行既有 validation。
- [ ] 保留所有低階 commands；新 façade 不接受 caller-supplied IDs、status 或 timestamps。
- [ ] 加入 initial create、active change、multi-change evolve、existing-draft update、collision、missing
  decision、policy/dependency error 與 dry-run tests。

**Verification**

```bash
uv run pytest tests/test_workflow_authoring.py
uv run trading workflow validate --all
uv run ruff check src/trading/core/workflow_authoring.py src/trading/cli.py tests/test_workflow_authoring.py
uv run ruff format --check src/trading/core/workflow_authoring.py src/trading/cli.py tests/test_workflow_authoring.py
```

## Work package 3: Bounded authoring safety

**Primary files**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `.gitignore` only if the chosen temporary path is not already local-only
- Modify: `docs/ARCHITECTURE.md`

- [ ] 新增 authoring-scoped repository lock 與 re-entrant lease，避免同一 authoring process deadlock。
- [ ] 所有 authoring writers 在 lock 內重讀 preconditions；study/qualification writers 維持現狀。
- [ ] Stage complete after tree，對 overlay 執行與 canonical 相同的 validator。
- [ ] 發布前比較 planned target digests；任何 target drift 都 zero mutation fail closed。
- [ ] Inject failure before/after each publish step，證明同-process exception 可回復 exact before bytes。
- [ ] Process-crash characterization test 固定 MVP 邊界：partial worktree 必須被下一次 validation 擋住，
  不宣稱 durable recovery。
- [ ] 測試 concurrent create/create、change/change、evolve/evolve 與 sync/release；結果只能是一個成功、
  另一個以可解釋 conflict 失敗，不得產生 duplicate identity。
- [ ] Temporary staging 不得包含 credentials、broker exports、private ledgers、market data 或 results。

**Verification**

```bash
uv run pytest tests/test_workflow_authoring.py
uv run trading workflow validate --all
uv run ruff check src/ tests/test_workflow_authoring.py
uv run ruff format --check src/ tests/test_workflow_authoring.py
```

## Work package 4: End-to-end verification and handoff

**Primary files**

- Modify: `tests/test_workflow_authoring.py`
- Modify: `CLAUDE.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `workflows/README.md` human-facing command guidance only if generated metadata is unchanged

- [ ] 在 isolated temporary repository 驗證 create → change → decision → evolve → release preparation。
- [ ] 驗證 abandon 與 retire 繼續使用既有低階安全行為；MVP 不新增 lifecycle semantics。
- [ ] 驗證 legacy v001-v008、所有既有 changes/studies/releases bytes 未被修改。
- [ ] 驗證 source disposition 預設 keep；move/pointer/remove 仍需 exact path 與個別確認。
- [ ] 驗證新文件只描述 happy paths，低階 commands 保留 compatibility/diagnostic 說明。
- [ ] 執行 full workflow validation、focused tests、full tests、Ruff、skill validation 與 diff audit。

**Verification**

```bash
uv run pytest tests/test_workflow_authoring.py
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run trading workflow validate --all
git diff --check
git diff -- workflows/strategy-forward-replication-research--v001 \
  workflows/strategy-forward-replication-research--v002 \
  workflows/strategy-forward-replication-research--v003 \
  workflows/strategy-forward-replication-research--v004 \
  workflows/strategy-forward-replication-research--v005 \
  workflows/strategy-forward-replication-research--v006 \
  workflows/strategy-forward-replication-research--v007 \
  workflows/strategy-forward-replication-research--v008
```

Expected final diff under released workflow paths: empty.

## Completion criteria

- Authoring users operate on intent/preview/approval instead of IDs/templates/registry/indexes。
- Initial create、active change 與 accepted-change evolve 都有 dry-run 與 tested happy path。
- Existing schema 1 registry、legacy change records、release evidence 與 low-level commands remain
  compatible。
- Released workflows、studies、results、qualification evidence 與 trading authority remain unchanged。
- Human approval and independent review boundaries are unchanged。
- Authoring target drift、ordinary exceptions 與 concurrent duplicate allocations fail safely。
- Documentation contains one current implementation plan；abandoned transaction/schema-v2 design
  diagrams are not retained as competing guidance。
- All verification commands pass。

## Deferred governance backlog

Each item below requires a separate proposal with its own problem statement and evidence that the MVP
cannot solve it:

1. Single-file `CHANGE.md` schema v2 and permanent dual-schema readers。
2. Durable authoring WAL、crash roll-forward and abort audit。
3. Cross workflow/study/qualification lock ordering and journal recovery。
4. Complete reachable-ref/blob identity proof or durable reservation ledger。
5. Persisted cross-version revisit dispositions and single-use consumption artifacts。
6. Legacy revisit cutover manifest。
7. Root registry schema migration and retirement evidence redesign。
8. Effective-release remote-tracking proof beyond the existing canonical-branch contract。
9. Physical deletion/adoption/tombstone flow for unregistered workflow drafts。

## Recommended delivery sequence

1. **PR 1:** Work package 1 only. Progressive disclosure and compatibility baselines。
2. **PR 2:** Work packages 2–3 together. High-level façade plus bounded authoring safety。
3. **PR 3:** Work package 4. Full verification and documentation handoff。

No PR in this sequence changes a released workflow or authorizes a study/trading action.
