# Workflow-First Research Architecture Implementation Plan

**Goal:** Establish the stage-one workflow-first boundary, versioned executable policy families,
workflow-native research definitions, and a frozen legacy experiment inventory without migrating
existing strategies.

**Architecture:** Add a policy registry parallel to the workflow registry, pin released policy
identities into workflow releases and research-definition snapshots, place new research code under
`src/trading/research_definitions/`, and make the existing experiment registry a closed legacy
inventory. Reuse current market-data, execution, evidence, and workflow infrastructure.

**Design source:**
`docs/superpowers/specs/2026-08-12-workflow-first-research-architecture-design.md`

## Global constraints

- Do not edit `pm/`.
- Do not migrate, rename, delete, or semantically change an existing experiment or retained result.
- Do not run a research study or claim a strategy outcome.
- Use test-first implementation for every executable contract and guard.
- Update `docs/ARCHITECTURE.md` in the same task that introduces or repurposes each path.
- Preserve current fail-closed market-data, execution, qualification, cutover, and drift behavior.
- Policy and workflow release operations require separate explicit approval with a stable human ID;
  implementation work must stop at a validated draft when that approval is absent.
- Run focused tests after every task and the full relevant suite before release preparation.

## Task 1: Add the policy domain and repository contract

**Files:**

- Create: `src/trading/core/policy_authoring.py`
- Create: `tests/test_policy_authoring.py`
- Create: `policies/README.md`
- Create: `docs/policies.md`
- Modify: `src/trading/cli.py`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `CLAUDE.md`

**Interfaces:**

- `PolicyRepository.validate_all()` validates registry, version directories, metadata, schemas,
  indexes, lifecycle, release evidence, dependency digests, and immutable released artifacts.
- `PolicyRepository.sync()` deterministically rebuilds generated indexes.
- `PolicyRepository.release(path, approved_by=...)` prepares current-time release evidence.
- CLI: `trading policy validate [PATH|--all]`, `trading policy sync`, and
  `trading policy release PATH --approved-by ID`.

- [ ] Write failing tests for empty registry validity, stale indexes, invalid names and schemas,
  draft release, immutable digest checking, supersession, retirement, and stable human approval.
- [ ] Implement the smallest policy repository and CLI needed to pass those tests, reusing canonical
  timestamp, JSON, Markdown, hashing, and atomic-write primitives where appropriate.
- [ ] Document lifecycle semantics: superseded releases remain resolvable by existing workflows;
  retired releases cannot be selected by a new workflow release.
- [ ] Run:

```bash
uv run pytest tests/test_policy_authoring.py
uv run trading policy sync
uv run trading policy validate --all
```

Expected: focused tests pass and the empty/new registry is structurally valid.

## Task 2: Define policy package schemas and runtime resolution

**Files:**

- Create: `src/trading/policies/__init__.py`
- Create: `src/trading/policies/models.py`
- Create: `src/trading/policies/resolver.py`
- Create: `tests/policies/test_policy_models.py`
- Create: `tests/policies/test_policy_resolver.py`
- Modify: `src/trading/core/policy_authoring.py`
- Modify: `docs/policies.md`
- Modify: `docs/ARCHITECTURE.md`

**Interfaces:**

- Typed `PolicyIdentity`, `PolicyRelease`, and family-specific configuration values.
- `PolicyResolver.resolve(family, version)` returns only a verified released policy.
- `PolicySet` rejects duplicate families and exposes a deterministic composite identity.
- Release metadata lists and hashes `POLICY.md`, `policy.yaml`, implementation paths, and
  conformance-test paths.

- [ ] Write failing tests for canonical identity, family/version mismatch, unreleased selection,
  duplicate families, modified dependencies, incompatible composition, and deterministic composite
  identity.
- [ ] Implement strict YAML decoding with unknown-field rejection and canonical Decimal/text
  handling where numeric policy values affect evidence.
- [ ] Ensure resolver reads tracked policy artifacts only; it must not use mutable defaults or
  silently resolve `latest`.
- [ ] Run:

```bash
uv run pytest tests/policies/test_policy_models.py tests/policies/test_policy_resolver.py
```

Expected: every policy selection is explicit, released, immutable, and deterministic.

## Task 3: Publish the four initial policy drafts and conformance suites

**Files:**

- Create: `policies/us-equity-market--v001/{README.md,POLICY.md,policy.yaml}`
- Create: `policies/firstrade-manual-trading--v001/{README.md,POLICY.md,policy.yaml}`
- Create: `policies/canonical-execution--v001/{README.md,POLICY.md,policy.yaml}`
- Create: `policies/portfolio-risk--v001/{README.md,POLICY.md,policy.yaml}`
- Create: `tests/policies/test_us_equity_market_v001.py`
- Create: `tests/policies/test_firstrade_manual_trading_v001.py`
- Create: `tests/policies/test_canonical_execution_v001.py`
- Create: `tests/policies/test_portfolio_risk_v001.py`
- Modify: `policies/README.md`
- Modify: relevant existing technical documents only to replace duplicated authority with precise
  policy references after parity is proven
- Modify: `docs/ARCHITECTURE.md`

**Inputs to preserve:**

- `.agents/rules/execution-model.md`
- `docs/market-data.md`
- `docs/canonical-sleeve-execution.md`
- `docs/manual-execution-ledger.md`
- `docs/controlled-followup-cutover.md`
- `docs/live-drift-and-recovery.md`
- existing calendar, execution, ledger, reconciliation, cutover, and risk tests

- [ ] Inventory every normative rule from the inputs and assign it to exactly one policy family or
  explicitly retain it as workflow-specific.
- [ ] Write failing conformance tests around the existing executable behavior before extracting
  configuration.
- [ ] Create complete draft policy contracts and strict machine-readable configurations without
  weakening current behavior.
- [ ] Prove policy-to-implementation parity with the existing focused suites.
- [ ] Run `trading policy sync` and `trading policy validate --all` after every policy mutation.
- [ ] Stop with four validated drafts unless the user separately supplies a stable human ID and
  explicitly approves release preparation.

Expected: the contracts are complete, machine-readable, and behaviorally equivalent to current
rules; no release is inferred from approval of this implementation plan.

## Task 4: Pin policy releases into workflows

**Files:**

- Modify: `src/trading/core/workflow_authoring.py`
- Modify: `tests/test_workflow_authoring.py`
- Modify: `.agents/skills/trading-author-workflow/references/workflow-authoring-contract.md`
- Modify: `.agents/skills/trading-author-workflow/assets/workflow-version/README.md`
- Modify: `docs/ARCHITECTURE.md` if workflow metadata responsibility changes materially

**Interfaces:**

- Workflow README metadata gains an explicit `policies` list containing family, version, path, and
  expected policy release digest.
- Workflow `RELEASE.json` embeds the verified policy identities and digests.
- Existing `dependencies` remain for non-policy normative/reference documents.

- [ ] Write failing tests for missing required families, unreleased/retired policy selection,
  duplicate family selection, policy digest drift, two workflows selecting different versions,
  and deterministic release evidence.
- [ ] Implement release-time policy resolution and fail-closed composition validation.
- [ ] Keep old workflow fixtures readable only where required for repository migration; do not let
  compatibility parsing authorize a new release without explicit policies.
- [ ] Run:

```bash
uv run pytest tests/test_policy_authoring.py tests/policies tests/test_workflow_authoring.py
uv run trading workflow validate --all
```

Expected: a workflow release cannot rely on mutable shared rules, and parallel workflows can pin
different released versions of the same family.

## Task 5: Introduce workflow-native research definitions

**Files:**

- Create: `src/trading/research_definitions/__init__.py`
- Create: `src/trading/research_definitions/registry.py`
- Create: `src/trading/research_definitions/_template/`
- Create: `tests/test_research_definition_registry.py`
- Modify: `src/trading/research_data/definitions.py`
- Modify: `src/trading/research_data/models.py`
- Modify: affected result/manifest schemas and focused tests
- Modify: `docs/reproducibility.md`
- Modify: `docs/ARCHITECTURE.md`

**Interfaces:**

- A new definition registry owns only workflow-native trials and does not auto-import legacy
  experiment packages.
- Formal capture requires an exact verified `PolicySet` and stores each policy release identity,
  configuration digest, and composite policy-set identity in the semantic and exact snapshots.
- Study evidence links the definition snapshot; source code is never copied into `workflows/`.

- [ ] Write failing tests proving policy changes alter semantic identity, reporting-only changes do
  not, exact dirty source remains reconstructable, and legacy definitions remain readable.
- [ ] Implement the new source registry and extend snapshot schema with explicit compatibility
  handling for older snapshots.
- [ ] Add a synthetic workflow-native definition fixture; do not create a real strategy study.
- [ ] Run focused research-definition, run-coordinator, result-schema, and snapshot tests.

Expected: new definitions have a non-legacy source boundary and formal evidence contains exact
policy identities.

## Task 6: Freeze the legacy experiment inventory

**Files:**

- Create: `ci/legacy-experiment-inventory.json`
- Create: `tools/check_legacy_experiment_inventory.py`
- Create: `tests/test_legacy_experiment_inventory.py`
- Modify: CI configuration that runs repository checks
- Modify: `src/trading/experiments/__init__.py` comments/documentation without changing discovery
  behavior required by existing consumers
- Modify: `docs/ARCHITECTURE.md`

**Interfaces:**

- The tracked inventory records every legacy package identity present at the stage-one baseline.
- The checker permits removal but rejects additions and rename-based replacement.
- New formal definitions are accepted only under `src/trading/research_definitions/`.

- [ ] Capture the exact current experiment package inventory without modifying packages.
- [ ] Write failing tests for addition, rename, duplicate identity, malformed inventory, and
  monotonic removal.
- [ ] Implement the checker and add it to CI.
- [ ] Verify current legacy imports, CLI listing, representative historical runs, and snapshot
  parity tests remain unchanged.

Expected: no new legacy experiment can enter through auto-discovery, while existing identities
remain available for compatibility and reproduction.

## Task 7: Update routing, skills, and the draft workflow

**Files:**

- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `README.md`
- Modify: `.agents/skills/trading-operate-workflow/SKILL.md`
- Modify: legacy experiment skills whose triggers currently create or mutate research identities
- Modify: `workflows/strategy-forward-replication-research--v001/README.md`
- Modify: `workflows/strategy-forward-replication-research--v001/WORKFLOW.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] Route new asset and new strategy requests to a released workflow plus study instead of
  `src/trading/experiments/`.
- [ ] Preserve clearly labeled legacy operations for existing identities, historical reproduction,
  and bounded migration.
- [ ] Replace the draft workflow's mutable normative document dependencies with exact policy
  identities while retaining necessary reference documents.
- [ ] Add the workflow-native definition, policy identity, legacy provenance, and source-snapshot
  requirements to the complete workflow contract.
- [ ] Run skill validation, workflow sync, and full workflow validation.

Expected: repository instructions have one unambiguous new-research route, and draft workflow v001
is complete and policy-aware.

## Task 8: Full stage-one verification and release boundary

**Files:**

- Verify all files changed by Tasks 1–7.
- Do not create policy or workflow `RELEASE.json` files without separate explicit approval.

- [ ] Run:

```bash
uv run pytest tests/test_policy_authoring.py tests/policies tests/test_workflow_authoring.py \
  tests/test_research_definition_registry.py tests/test_legacy_experiment_inventory.py
uv run pytest
uv run ruff check src/ tests/ tools/
uv run ruff format --check src/ tests/ tools/
uv run trading policy validate --all
uv run trading workflow sync
uv run trading workflow validate --all
git diff --check
git status --short
```

- [ ] Confirm no file under `pm/` changed, no legacy experiment/result identity changed, no study
  was created, and no private runtime data was added.
- [ ] Review the final diff against the design acceptance criteria.
- [ ] If and only if separately authorized with stable human identities, prepare policy releases
  first, update the workflow to their exact release digests, then prepare the workflow release.
- [ ] Re-run the complete validation suite after release preparation. Do not infer permission to
  commit, push, open a PR, or merge.

Expected: stage one is either a fully validated set of drafts or separately approved prepared
releases. It is not effective until the release commit reaches the canonical branch.
