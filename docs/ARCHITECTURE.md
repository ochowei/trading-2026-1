# Repository architecture and file guide

This document is the canonical map of the repository. It explains where each kind of source,
configuration, documentation, evidence, and local runtime state belongs. For large repeated
collections—experiments, results, tests, ADRs, and workflow studies—it documents the directory and
filename contract instead of maintaining a brittle inventory of every instance.

## Maintenance contract

Update this document in the same change whenever a tracked file or directory is added, removed,
moved, renamed, or given a materially different responsibility. Also update it when a new repeated
file pattern, public entry point, generated artifact, or local-only data boundary is introduced.

Routine additions that already fit a documented pattern do not require a new per-file entry. For
example, adding another `<experiment_name>/` package, `results/<experiment_name>/latest.json`, ADR,
or `test_*.py` only requires an update here if it changes that pattern or its responsibility.

## System shape

```text
CLI and automation
    -> experiment registry / followup workflows
    -> market-data validation and immutable snapshots
    -> strategy, signal, execution, and sleeve engines
    -> result validity, qualification, and local lifecycle state
    -> tracked research evidence and manual followup reports
```

The tracked repository contains code, contracts, reproducible research metadata, and selected
result evidence. Provider caches, protected immutable blobs, broker imports, credentials, and
manual trading state are deliberately local-only.

## Repository root

| Path | Purpose |
|---|---|
| `AGENTS.md` | Lightweight Agent router. Points Agents to the canonical rules and repository map, selects repository skills, and states non-negotiable guardrails. |
| `CLAUDE.md` | Canonical operating rules for Agents, required development commands, experiment rules, and documentation-maintenance obligations. |
| `GEMINI.md` | Minimal compatibility pointer that directs Gemini-based Agents to the canonical rules and repository map. |
| `CONTEXT.md` | Domain model and ubiquitous language for trading research concepts used across code and documentation. |
| `README.md` | Human-facing project introduction, usage guide, and high-level contracts for the research phases. |
| `pyproject.toml` | Python package metadata, runtime and development dependencies, `trading` console entry point, and Ruff configuration. |
| `uv.lock` | Locked dependency graph used by `uv` for reproducible environments. |
| `.python-version` | Project Python-version selection for compatible version managers. |
| `.gitignore` | Excludes caches, environments, private trading state, credentials, and non-retained results; explicitly allows retained research artifacts. |
| `config/` | Tracked repository configuration and executable validation contracts that are not application runtime code. |
| `legacy/` | Repository-level archive for retired source material retained for inspection or reproducibility; it is not an extension point for new research. |
| `legacy/README.md` | Defines the archive boundary and the checkout-only compatibility contract for legacy experiment source. |
| `legacy/experiments/` | Physical archive for the closed `ticker_NNN_description` experiment inventory. |
| `legacy/results/` | Read-only legacy-schema latest results and superseded result-directory names. Diagnostic comparison, explicit status, and documentation checks may fall back here; selection, authorization, qualification, freshness, formal evidence readers, and all writers remain canonical-only. |
| `policies/` | Versioned executable market, broker, execution, and portfolio policy registry. Released versions are immutable and selected explicitly by workflow releases. |
| `workflows/` | Versioned research procedures plus version-scoped changes and studies. |

## Agent and automation configuration

### `.agents/`

Repository-owned Agent knowledge and skills.

| Path | Purpose |
|---|---|
| `.agents/context/cross_asset_lessons.md` | Compact cross-asset lessons, prohibited directions, parameter-scaling guidance, and freshness metadata. |
| `.agents/context/cross_asset_evidence.md` | Detailed evidence supporting the compact cross-asset lessons. |
| `.agents/rules/execution-model.md` | Mandatory execution-model contract for non-grandfathered experiments. |
| `.agents/rules/workflow-study-governance.md` | Shared canonical workflow-study identity, lifecycle, authority-separation, evidence, privacy, and version-boundary rules used by operator and reviewer skills. |
| `.agents/skills/trading-*/SKILL.md` | Active workflow instructions for a specific repository research task. Legacy experiment skills are archived under `legacy/agent-skills/`. |
| `.agents/skills/trading-*/agents/openai.yaml` | Skill discovery metadata and default Agent presentation. |
| `.agents/skills/trading-*/assets/` | Templates copied or adapted by an active skill, currently used by workflow authoring. |
| `.agents/skills/trading-*/references/` | Detailed mode-specific contracts loaded through progressive disclosure only when an active skill workflow needs them. |

### `.claude/commands/`

Active Claude command definitions are no longer kept here. The former legacy experiment commands
are archived under `legacy/claude/commands/`; new cross-Agent workflows should normally live in
`.agents/skills/trading-*/`.

### `.github/workflows/`

| Path | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Runs Ruff checks plus workflow, policy, legacy-inventory, and market-data migration contract validation for pull requests and `main` pushes. |

## Documentation

### `docs/`

| Path | Purpose |
|---|---|
| `docs/ARCHITECTURE.md` | This canonical repository map and file-ownership guide. |
| `docs/market-data.md` | CSV market-data provider, cache, validation, freshness, and CLI contract. |
| `docs/reproducibility.md` | Immutable blobs, manifests, definitions, bundles, run modes, and garbage collection. |
| `docs/reproducibility-v008.md` | Normative v008 addendum for structured routes, human authority artifacts, deterministic exact-session derivation, tracked terminal evidence, and compatibility. |
| `docs/auxiliary-unavailable-decision-reproducibility.md` | Normative explicit-unavailable auxiliary manifest, replay, audit, and signal-suppression contract. |
| `docs/result-validity-and-trial-history.md` | Result schemas, validity states, evaluation boundaries, and append-only trial history. |
| `docs/canonical-sleeve-execution.md` | Canonical sleeve capital, execution-cost scenarios, metrics, and parity evidence. |
| `docs/manual-execution-ledger.md` | Manual ledger domain, integrity, broker reconciliation, and CLI contract. |
| `docs/historical-qualification-and-shadow.md` | Historical folds, benchmark gates, prospective Shadow evidence, and qualification lifecycle. |
| `docs/historical-qualification-and-shadow-v005.md` | Proposed v005 clean-evidence audit, retrospective-confirmatory checkpoint, workflow-native qualification, and unchanged Shadow boundary. |
| `docs/historical-qualification-and-shadow-v006.md` | Proposed v006 explicit retrospective role-calendar contract with backward-compatible Historical and Shadow boundaries. |
| `docs/historical-qualification-and-shadow-v007.md` | Released v007 frozen selection-boundary contract for clean and retrospective qualification. |
| `docs/historical-qualification-and-shadow-v008.md` | Versioned v008 exact-study readiness, explicit clean-calendar, study-time retrospective terminal-evidence, and unchanged Shadow-authority contract. |
| `docs/research-evidence-stages-and-outcomes.md` | Stable pointer to the full plus plain-language stage/outcome companion beside v008. |
| `docs/research-evidence-preservation.md` | Reference explanation of tracked content-addressed candidate-freeze/qualification evidence, recoverable publication, and permanent-retention implementation. |
| `docs/result-validity-and-trial-history-v005.md` | Proposed v005 result-validity extension for retrospective evidence roles while preserving legacy event verification. |
| `docs/controlled-followup-cutover.md` | Followup lifecycle, authorization, parity, rollback, and allocation epochs. |
| `docs/live-drift-and-recovery.md` | Frozen drift envelopes, health states, hard guards, checkpoints, and recovery. |
| `docs/phase-9-primary-followup-migration.md` | Primary followup migration boundaries, parity evidence, and verification. |
| `docs/strategy-forward-replication-research-workflow.md` | Human-readable design of the strategy replication and promotion research workflow. |
| `docs/workflow-governance/README.md` | Human-facing entry point linking canonical workflow authority, workflow skills, governance diagrams, their scope, and the final review conclusion. |
| `docs/workflow-governance/workflow-governance-flow.html` | Standalone B1 high-level sequence visualization of workflow authoring, release, study-operation, and review role handoffs. |
| `docs/workflow-governance/workflow-governance-layers.html` | Standalone A1 inter-layer governance flow with decisions and recovery paths, plus A2 native expandable internal-state references for workflow design, release authority, and study review. |
| `docs/policies.md` | Policy registry, release, resolution, composition, and privacy contract. |
| `docs/adr/NNNN-*.md` | Immutable Architecture Decision Records explaining important design choices and their consequences. |
| `docs/superpowers/specs/YYYY-MM-DD-*.md` | Historical feature/design specifications retained as implementation context. |
| `docs/superpowers/plans/YYYY-MM-DD-*.md` | Historical approved implementation plans retained as execution context. |

### `pm/`

Human-maintained product-management material. Agents must not edit this directory unless the user
explicitly designates the task as `HUMAN_PM_HELPER`.

| Path | Purpose |
|---|---|
| `pm/HUMAN_PM_MEMO.md` | Watch list, strategy ideas, execution notes, and human-maintained change history. |
| `pm/USE_CASES.md` | Human workflows and common-operation index. |

## Application source

All installable Python code lives under `src/trading/`. `src/trading/__init__.py` marks the package;
`pyproject.toml` exposes `trading.cli:main` as the `trading` command.

### Top-level application modules

| Path | Purpose |
|---|---|
| `src/trading/cli.py` | Unified command parser and dispatcher for experiments, workflow-native research definitions, results, data, ledger, qualification, followup lifecycle, drift, versioned policies, and versioned workflows. |
| `src/trading/followup.py` | Selected-strategy definitions and generation of manual Firstrade followup signals/order instructions. |
| `src/trading/followup_backtest.py` | Portfolio-level simulation of the followup set, including equal sleeves, daily equity, and structured reporting. |

### `src/trading/core/`

Shared domain and orchestration code. Experiment packages should reuse these components instead of
creating parallel infrastructure.

| File | Purpose |
|---|---|
| `accounting.py` | Decimal-safe amounts, canonical JSON, and UTC timestamp primitives. |
| `base_config.py` | Base `ExperimentConfig` value object. |
| `base_signal_detector.py` | Abstract signal-detector interface and common signal behavior. |
| `base_backtester.py` | Legacy/general backtest engine for stops, targets, and expiry. |
| `base_strategy.py` | Base fetch → indicator → signal → backtest → report orchestration. |
| `execution_backtester.py` | Required execution-model engine, including entry/exit modes, slippage, intraday ambiguity, and unfilled orders. |
| `execution_strategy.py` | Strategy base that connects experiments to the execution-model engine and reporting. |
| `sleeve_engine.py` | Canonical sleeve evaluation, daily equity, base/stress costs, metrics, and parity evidence. |
| `bundle_strategy.py` | Provider-free strategy seams for primary and auxiliary snapshot bundles. |
| `data_fetcher.py` | Backward-compatible multi-ticker facade over validated market-data services. |
| `performance_analyzer.py` | Rolling-window performance and stability analysis. |
| `results.py` | Result persistence, reading, validity diagnostics, and experiment comparison. |
| `freshness.py` | Read-only knowledge freshness and persisted-result validity scans. |
| `definition_resolver.py` | Read-only resolution of an experiment's current semantic definition. |
| `evaluation.py` | Explicit stale-result refresh and fail-closed per-asset ranking boundary. |
| `sync_docs.py` | Checks synchronization between experiment Markdown metrics and retained results. |
| `ledger_csv.py` | Fixed-schema canonical CSV encoding/decoding for manual ledger data. |
| `ledger_storage.py` | Private atomic writes and bounded filesystem locking. |
| `broker_reconciliation.py` | Broker-export parsing and comparison against canonical accounting state. |
| `manual_ledger.py` | Manual trading ledger domain, hash-chain replay, verification, and persistence. |
| `proposals.py` | Decimal-safe proposal terms and deterministic proposal identities. |
| `followup_proposals.py` | Builds dry-run entry and exit proposals from a verified ledger. |
| `followup_data.py` | Declared followup auxiliary data, as-of alignment, and bundle identity. |
| `followup_cutover.py` | Controlled followup lifecycle, authorization, parity, and reporting. |
| `live_drift.py` | Frozen drift envelopes, metric evaluation, checkpoints, and recovery rules. |
| `live_drift_registry.py` | Private append-only drift evidence, hash-chain replay, and storage locking. |
| `qualification.py` | Historical screens, benchmark/selection adjustment, Shadow evidence, and gates. |
| `qualification_workflow.py` | Workflow-native or frozen-legacy qualification identity resolution, clean/retrospective plan registration, and deterministic screen orchestration. |
| `qualification_transaction.py` | Durable journal, idempotent recovery, shared journal identity, and serialized publication for one complete-family trial registration plus its exact qualification plan. |
| `study_qualification.py` | Exact-study qualification compiler, structured preregistration spec, release-capability enforcement, and backward-compatible v004/S004 adapter. |
| `study_terminal_evidence.py` | Terminal study-time evidence linkage across frozen study artifacts, typed canonical qualification plan/screen replay, current-head Development absence proofs, and independently supported required-challenge observations. |
| `workflow_authoring.py` | Closed high-level create/change/evolve requests, deterministic mutation previews, versioned workflow metadata, hashing, indexes, releases, and lifecycle transitions. |
| `workflow_studies.py` | Study scaffolding, preregistration, stage transitions, evidence, and completion, including serialization of Development terminal failure against qualification registration. |
| `policy_authoring.py` | Versioned policy registry validation, synchronization, conformance execution, immutable releases, and lifecycle evidence. |
| `legacy_experiments.py` | Closed-inventory scan and monotonic-removal guard for legacy experiment identities. |
| `__init__.py` | Package marker; shared APIs are normally imported from their defining modules. |

### `src/trading/market_data/`

Fail-closed boundary around Yahoo adjusted daily OHLCV and the validated local cache.

| File | Purpose |
|---|---|
| `contracts.py` | Calendar/reader protocols and refresh vocabulary. |
| `models.py` | Market series, requirements, availability policies, decisions, and metadata values. |
| `provider.py` | Provider protocol and Yahoo Finance adapter. |
| `calendar.py` | XNYS sessions, historical special closures, and actual-close cutoffs. |
| `availability.py` | Explicit excess-observation-lag modes, including auditable unavailable auxiliary decisions. |
| `validation.py` | Schema, OHLCV, finiteness, uniqueness, and exact-session validation. |
| `cache.py` | Canonical CSV/sidecar storage, locks, atomic publication, and quarantine. |
| `service.py` | Fresh reuse plus incremental/full refresh orchestration. |
| `bundle.py` | Read-only bundles and backward as-of alignment of auxiliary series. |
| `migration_policy.py` | Scans experiment data access and enforces the shrinking legacy bypass allowlist. |
| `__init__.py` | Curated public market-data API exports. |

### `src/trading/research_data/`

Immutable reproducibility evidence and formal run coordination.

| File | Purpose |
|---|---|
| `artifacts.py` | Shared immutable publication, checksums, and semantic verification. |
| `evidence.py` | Add-only publication and digest resolution for tracked candidate-freeze evidence and replayable source-identified qualification registry/checkpoint snapshots. |
| `models.py` | Typed blob, manifest, definition, run, and garbage-collection values. |
| `manifest_codec.py` | Strict canonical manifest encoding and snapshot identity. |
| `store.py` | Snapshot publication, verification, portable bundles, references, and garbage collection. |
| `definitions.py` | Semantic fingerprints and exact-source definition blobs, including dirty-worktree capture. |
| `result_schema.py` | Versioned result payloads, computed validity, and legacy compatibility. |
| `runs.py` | Online, offline, migration, and ephemeral run/publication boundaries, including exact workflow-native observation provenance supplied by the CLI. |
| `migration.py` | Immutable parity-linked migration-result publication. |
| `parity.py` | Fixed-snapshot parity evidence and immutable parity artifacts. |
| `trial_registry.py` | Append-only experiment trial identities, observations, and tombstones. |
| `qualification_registry.py` | Local append-only Historical and Shadow lifecycle evidence, including canonical single plan/screen identities and empty-registry initialization for authoritative absence proofs. |
| `__init__.py` | Curated public research-data API exports. |

### `src/trading/policies/`

Runtime values and fail-closed resolution for released executable policies.

| File | Purpose |
|---|---|
| `models.py` | Exact policy identities and verified release values. |
| `resolver.py` | Exact family/version resolution, digest verification, duplicate-family rejection, and deterministic composite policy-set identity. |
| `__init__.py` | Curated public policy API. |

### `src/trading/research_definitions/`

Workflow-native research source. New formal trials belong here rather than in the closed legacy
experiment tree.

| Pattern | Purpose |
|---|---|
| `registry.py` | Resolves and explicitly loads lowercase `<family>/<trial>` source identities without importing legacy experiments. |
| `execution.py` | Verifies one released workflow and resolves its four exact policy pins into the composite policy set required for definition capture and formal execution; also provides release-local policy resolution for nested study validation without recursively re-entering study validation. |
| `daily_bar.py` | Reusable primary-only daily-bar definition seam for declarative workflow-native trials, producing gross candidate trades for canonical sleeve evaluation. |
| `monthly_calendar.py` | Reusable primary-only monthly-calendar definition seam with frozen XNYS entry-session and fixed-holding semantics for workflow-native trials. |
| `rate_volatility_pullback.py` | Reusable primary-plus-backward-as-of-auxiliary pullback definition seam with fixed next-open execution and MOVE-direction gating. |
| `rate_volatility_pullback_gap_safe.py` | Explicitly suppresses workflow-native signals on over-age auxiliary decisions while preserving lag audit evidence. |
| `profit_protection_pullback.py` | Reusable primary-only XLF pullback seam with close-armed profit protection, next-open exits, and a fixed occupation lock that preserves paired entry cohorts. |
| `fxi_mean_reversion.py` | Reusable FXI pullback/WR, ATR-band, and same-session ASHR-divergence definition seam with next-open entry, pessimistic target/stop resolution, cooldown, and fixed expiry semantics. |
| `_template/` | Starting structure for a workflow-native definition. |
| `<family>/<trial>/definition.py` | Stable source entry point for one permanent workflow-governed trial identity. |

### `src/trading/experiments/`

This is the compatibility registry and documentation area for the closed legacy inventory.
Archived source packages live under repository-root `legacy/experiments/`, while the registry
extends its package search path in a repository checkout so their historical import identities remain
`trading.experiments.<experiment_name>`. It auto-imports every inventoried package whose name does
not start with `_`; each package's `__init__.py` registers its strategy. CI scans the archive and
rejects new or renamed identities. New formal research uses `src/trading/research_definitions/`.

| Pattern | Purpose |
|---|---|
| `src/trading/experiments/__init__.py` | Registry, registration decorator, lookup/list APIs, and `pkgutil` auto-discovery. |
| `src/trading/experiments/_template/` | Historical package template retained for reference; it must not be used to add a legacy identity. |
| `src/trading/experiments/EXPERIMENTS_<TICKER>.md` | Per-asset experiment overview, result table, parameter comparison, and machine-oriented `AI_CONTEXT`. |
| `legacy/experiments/<experiment_name>/config.py` | Experiment identity, ticker, periods, thresholds, exits, and other parameters. |
| `legacy/experiments/<experiment_name>/signal_detector.py` | Indicators and entry-signal logic. |
| `legacy/experiments/<experiment_name>/strategy.py` | Connects config, detector, data declarations, execution, and formal research hooks. |
| `legacy/experiments/<experiment_name>/__init__.py` | Registers the strategy under its unchanged CLI and import identity. |

## Tests and repository checks

| Path | Purpose |
|---|---|
| `tests/conftest.py` | Shared pytest setup and fixtures. |
| `tests/test_*.py` | Behavioral and contract tests, generally named after the module or lifecycle being protected. Snapshot-contract tests pin migration behavior for selected experiments. |
| `tests/policies/test_*.py` | Policy resolution, composition, definition-identity, and version-specific conformance tests. |
| `config/repository-checks/README.md` | Maintenance contract for active repository-wide checks and their tracked configuration. |
| `tools/check_experiment_market_data_access.py` | CI scanner that detects experiment access which bypasses the declared market-data boundary. |
| `config/repository-checks/check_legacy_experiment_inventory.py` | CI entry point that rejects additions or rename-based replacements in the legacy experiment tree. |
| `config/repository-checks/legacy-experiment-inventory.json` | Sorted stage-one baseline of frozen legacy experiment package identities; removals are allowed but additions are not. |
| `ci/market-data-bypass-allowlist.json` | Typed, shrinking baseline of legacy experiment bypasses permitted during migration. |

Tests may contain explicit synthetic broker fixtures. Real broker exports, credentials, and personal
trading data must never be placed in `tests/` or committed anywhere.

## Research results and workflow registry

### `policies/`

| Pattern | Purpose |
|---|---|
| `policies/README.md` | Policy lifecycle authority and generated registry index. |
| `policies/<family>--vNNN/README.md` | Version identity plus implementation and conformance paths. |
| `policies/<family>--vNNN/POLICY.md` | Self-contained human-readable policy contract. |
| `policies/<family>--vNNN/policy.yaml` | Strict machine-readable family configuration. |
| `policies/<family>--vNNN/RELEASE.json` | Human-approved immutable release evidence, present only after release preparation. |

### `results/`

| Pattern | Purpose |
|---|---|
| `results/<experiment_name>/latest.json` | Canonical retained latest result consumed by validity, selection, authorization, and formal workflows; diagnostic readers prefer it over any archived duplicate. |
| `results/<experiment_name>/prev_1.json`, `prev_2.json` | Retained recent predecessors when present. |
| `results/<experiment_name>/<snapshot_id>.snapshot.json` | Retained immutable snapshot manifest used for reproducible formal execution. |
| `results/<experiment_name>/<timestamp>.json` | Historical run output; most such files are ignored unless explicitly retained by repository policy. |
| `results/<research-family>--<stage>-gate/<study-id>.json` | Tracked workflow-study stage-gate calculation that binds frozen rules to exact formal observation identities and checksums. |
| `results/research-evidence/<sha256>.md` | Permanently retained, tracked, content-addressed pre-freeze research evidence referenced by immutable candidate-freeze records. |
| `results/qualification-evidence/<sha256>.json` | Permanently retained, tracked, self-contained source-identified qualification registry/checkpoint snapshot replayed through the authoritative hash-chain reader for terminal study decisions and Development absence proofs. |
| `results/study-evidence/**` | Permanently retained, tracked Development gates, typed challenge manifests, and distinct challenge evidence artifacts used by terminal study-time review. |
| `results/trial_registry.json` | Tracked append-only experiment-family/trial inventory and formal observations. |

Never treat `latest.json` as valid solely because it exists; validity is recomputed against its data
and semantic definition references.

Legacy-schema latest results and superseded aliases are retained under `legacy/results/`. Only
comparison, explicit result-status, and documentation diagnostics may fall back there. Freshness,
evaluation/ranking, followup, Shadow/Active, qualification, formal evidence verification, and all
writers use canonical `results/` exclusively. See `legacy/README.md` for the archive contract and
historical alias map.

### `workflows/`

Versioned, tracked research-workflow registry shared by humans and Agents.

| Pattern | Purpose |
|---|---|
| `workflows/README.md` | Version lifecycle authority and generated registry index. |
| `workflows/<slug>--vNNN/README.md` | Version metadata, state, checksums, release evidence, and generated study/change indexes. |
| `workflows/<slug>--vNNN/WORKFLOW.md` | Self-contained workflow contract pinned by studies. |
| `workflows/<slug>--vNNN/STAGES_AND_OUTCOMES.md` | Optional version companion containing full and plain-language stage/outcome guidance; when declared `reference` plus `pinned: true`, release evidence fixes its exact bytes while `WORKFLOW.md` remains the sole behavioral authority. |
| `workflows/<slug>--vNNN/work/studies/<study>/` | Route/spec, preregistered plan, add-only Development authorization, candidate freeze, metadata, evidence, conclusion, and outcome for a workflow study when present. |
| `workflows/<slug>--vNNN/work/changes/<change>/` | Proposed workflow change, impact, decision, and validation evidence when present. |
| `workflows/.authoring.lock` | Ignored local advisory lock shared only by workflow authoring writers; it is not lifecycle evidence or repository authority. |

Workflow metadata and generated indexes must be changed through the authoring/study services or
their repository skills, not hand-edited casually.

`trading workflow create`, `trading workflow change create`, and `trading workflow evolve` are the
public happy-path authoring façade. Their closed JSON request files are ephemeral operation inputs,
not tracked lifecycle authority: callers supply confirmed content and exact pins, while the CLI
allocates `vNNN`/`Cxxx`, writes the existing schema-1 and five-file formats, synchronizes indexes,
and validates. The façade reads and retains request/source files; moving, replacing with a pointer,
or removing a source is a separate exact-path operation that requires individual human confirmation.
Low-level transition and sync commands remain compatibility/diagnostic entry points, while guarded
decision and release commands remain separate human-authority seams rather than alternate authoring
happy paths.

High-level apply holds the re-entrant authoring lease, verifies the previewed target digests, copies
only the workflow tree into a system temporary directory, applies and validates the complete staged
after-tree against canonical repository dependencies, then rechecks target digests before atomic
per-file publication. Ordinary in-process publication failures restore the exact before bytes and
revalidate. A process crash can still leave a partial worktree; the next authoring writer fails
closed on structural validation and requires manual inspection. This bounded mechanism is not a
durable journal and does not coordinate study or qualification writers.

Workflow releases pin exact released policy family/version identities and `RELEASE.json` digests.
Studies inherit those immutable selections from their workflow version and record the composite
policy-set identity in formal definition evidence.

## Local-only runtime directories

These paths are intentionally ignored and must not be committed. Their absence in a fresh clone is
normal.

| Path | Purpose |
|---|---|
| `.venv/` | Local `uv` Python environment. |
| `workflows/.authoring.lock` | Local workflow-authoring coordination file; safe to recreate and never tracked. |
| `.cache/market-data/` | Validated active provider CSV data and metadata sidecars. |
| `.cache/market-data-quarantine/` | Corrupt or rejected cache generations retained for diagnosis. |
| `.research-data/blobs/` | Protected content-addressed data and research-definition blobs referenced by manifests. |
| `state/` | Manual ledger, reconciliation, qualification, followup lifecycle, live-drift evidence, heads, and locks. |
| `broker-imports/`, `.broker-imports/` | Local real broker exports used for reconciliation. |
| `credentials/`, `.credentials/`, `secrets/` | Local secrets and provider/broker credentials. |
| `.pytest_cache/`, `.ruff_cache/`, `__pycache__/` | Regenerable test, lint, and Python caches. |

The root `.codex/` directory, when present locally, contains workspace tooling metadata rather than
application architecture and is not a source of project rules.

## Where to make a change

| Change | Primary location | Usually update too |
|---|---|---|
| Maintain or reproduce a legacy experiment | Existing `legacy/experiments/<identity>/` | Preserve semantic identity, per-asset overview, tests, and result evidence; do not add or rename a package. |
| Add a new research identity | `src/trading/research_definitions/` | Released workflow/study, exact policy versions, immutable definition/data evidence, tests. Never add a legacy experiment package. |
| Add or revise reusable research constraints | `policies/` and `src/trading/policies/` | Conformance tests, affected workflow version, `docs/policies.md`, and technical docs. |
| Change shared strategy/backtest behavior | `src/trading/core/` | Focused tests, affected phase docs, and experiment docs if metrics or contracts change. |
| Change provider/cache behavior | `src/trading/market_data/` | `docs/market-data.md`, tests, ADR when architectural. |
| Change snapshots/results/formal runs | `src/trading/research_data/` | Reproducibility/result docs, tests, ADR when architectural. |
| Change CLI behavior | `src/trading/cli.py` | `CLAUDE.md` commands, `README.md`, relevant contract docs, and CLI tests. |
| Change followup selection or reporting | `src/trading/followup.py` / `followup_backtest.py` | Followup tests and relevant experiment/result docs. |
| Change a repository workflow contract | `workflows/` | Use `trading-author-workflow`; generated indexes and release evidence must remain valid. |
| Change repository layout or ownership | Affected paths | Update this document in the same change. |

Versioned Phase 6 workflow contracts live at
`docs/historical-qualification-and-shadow-vNNN.md`. Each file is an immutable normative dependency
for the workflow version that pins it; behavioral changes create a new document version instead of
rewriting a document pinned by a released workflow.
