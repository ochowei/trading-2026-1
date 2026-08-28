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
example, adding another workflow-native trial artifact, ADR, or `test_*.py` only requires an update
here if it changes that pattern or its responsibility. The legacy experiment inventory is retired
and does not accept additions or new results.

## System shape

```text
CLI and automation
    -> workflow-native research / retired-legacy diagnostics / followup exits
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
| `legacy/experiment-overviews/` | Archived per-asset `EXPERIMENTS_<TICKER>.md` tables and AI context. They are historical evidence, not workflow outcome authority. |
| `legacy/templates/experiment/` | Former legacy experiment package template retained outside installable and auto-discovery paths for historical inspection only. |
| `legacy/results/` | Read-only terminal archive for every retired legacy result class: last retained latest results, immutable snapshot manifests, retained formal runs, legacy-schema results, superseded aliases, and unreferenced history. Diagnostics may inspect archived latest files, but no writer, ranking, qualification, promotion, or new-entry authorization may consume this archive. |
| `policies/` | Versioned executable market, broker, execution, and portfolio policy registry. Released versions are immutable and selected explicitly by workflow releases. |
| `workflows/` | Versioned research procedures plus version-scoped changes and studies. |

## Agent and automation configuration

### `.agents/`

Repository-owned Agent knowledge and skills.

| Path | Purpose |
|---|---|
| `.agents/context/cross_asset_lessons.md` | Compact cross-asset lessons, prohibited directions, parameter-scaling guidance, and freshness metadata. |
| `.agents/context/cross_asset_evidence.md` | Detailed evidence supporting the compact cross-asset lessons. |
| `.agents/rules/execution-model.md` | Released-workflow-pinned execution-model dependency. Its current path and bytes are frozen; future changes require a versioned successor selected by a new workflow version. |
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
| `.github/workflows/ci.yml` | Runs Ruff, the non-slow fast regression suite, and workflow, policy, path-ownership, legacy-inventory, and market-data boundary validation for pull requests and `main` pushes. |
| `.github/workflows/legacy-conformance.yml` | Runs the full Primary frozen-inventory matrix for relevant shared-runtime PRs, every `main` push, daily at 09:00 UTC, and manual dispatch. |
| `.github/workflows/auxiliary-legacy-conformance.yml` | Runs the full 240-case Auxiliary matrix after high-risk path pushes to `main`, weekly on Monday at 09:00 UTC, on manual dispatch, or when a PR receives the `full-auxiliary-conformance` label. |

## Documentation

### `docs/`

| Path | Purpose |
|---|---|
| `docs/ARCHITECTURE.md` | This canonical repository map and file-ownership guide. |
| `docs/README.md` | Human-facing document status router that distinguishes current, version-pinned, compatibility, historical, and retired guidance without rewriting pinned bytes. |
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
| `docs/result-storage-layout-v009.md` | Normative categorized result namespaces, append-only path migration, historical compatibility resolution, canonical writer destinations, and retention boundary. |
| `docs/legacy-experiment-retirement-v010.md` | Terminal legacy-research retirement boundary, archived result authority, disabled public entry points, bounded v009-to-v010 path resolution, and existing-position exit compatibility. |
| `docs/result-validity-and-trial-history-v005.md` | Proposed v005 result-validity extension for retrospective evidence roles while preserving legacy event verification. |
| `docs/controlled-followup-cutover.md` | Followup lifecycle, authorization, parity, rollback, and allocation epochs. |
| `docs/live-drift-and-recovery.md` | Frozen drift envelopes, health states, hard guards, checkpoints, and recovery. |
| `docs/phase-9-primary-followup-migration.md` | Completed compatibility migration closure record with explicit retirement guidance for its historical commands. |
| `docs/strategy-forward-replication-research-workflow.md` | Human-readable design of the strategy replication and promotion research workflow. |
| `docs/workflow-governance/README.md` | Human-facing entry point linking canonical workflow authority, workflow skills, governance diagrams, their scope, and the final review conclusion. |
| `docs/workflow-governance/workflow-governance-flow.html` | Standalone B1 high-level sequence visualization of workflow authoring, release, study-operation, and review role handoffs. |
| `docs/workflow-governance/workflow-governance-layers.html` | Standalone A1 inter-layer governance flow with decisions and recovery paths, plus the strictly aligned A1-2 governance-control state machine. |
| `docs/policies.md` | Policy registry, release, resolution, composition, and privacy contract. |
| `docs/adr/NNNN-*.md` | Immutable Architecture Decision Records explaining important design choices and their consequences. |
| `docs/superpowers/specs/YYYY-MM-DD-*.md` | Historical feature/design specifications retained as implementation context. |
| `docs/superpowers/plans/YYYY-MM-DD-*.md` | Historical approved implementation plans retained as execution context. |

### `docs/pm/`

Human-maintained product-management material. Agents must not edit this directory unless the user
explicitly designates the task as `HUMAN_PM_HELPER`.

| Path | Purpose |
|---|---|
| `docs/pm/HUMAN_PM_MEMO.md` | Watch list, strategy ideas, execution notes, and human-maintained change history. |
| `docs/pm/USE_CASES.md` | Human workflows and common-operation index. |

## Application source

All installable Python code lives under `src/trading/`. `src/trading/__init__.py` marks the package;
`pyproject.toml` exposes `trading.cli:main` as the `trading` command.

### Top-level application modules

| Path | Purpose |
|---|---|
| `src/trading/cli.py` | Stable console entry point and unified dispatcher. Responsibility-specific parsers and handlers live under `src/trading/commands/`. |
| `src/trading/knowledge_freshness.py` | Aggregate active-knowledge plus explicitly labeled legacy-archive freshness report used by the compatibility `trading freshness` command. |
| `src/trading/followup.py` | Retired-strategy compatibility used only for fail-closed status reporting and exit handling of pre-existing manual positions; archived results cannot authorize new entries. |
| `src/trading/followup_backtest.py` | Retained implementation of the retired legacy followup simulation; its public CLI entry fails closed. |

### `src/trading/core/`

Mixed shared domain and compatibility code. Canonical ownership is documented by the local README;
new workflow-native definitions use maintained components without creating new legacy identities.

| File | Purpose |
|---|---|
| `README.md` | Local ownership map separating maintained shared infrastructure, policy-pinned implementations, legacy strategy compatibility, and workflow import aliases. |
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
| `performance_analyzer.py`, `results.py`, `freshness.py`, `definition_resolver.py`, `evaluation.py`, `sync_docs.py` | Module aliases preserving historical `trading.core.*` imports while canonical implementations live under `trading.legacy` or `trading.knowledge_freshness`. |
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
| `qualification_workflow.py`, `study_qualification.py`, `study_terminal_evidence.py`, `workflow_authoring.py`, `workflow_studies.py` | Module aliases preserving historical imports while canonical implementations live under `trading.workflow`. |
| `qualification_transaction.py` | Durable journal, idempotent recovery, shared journal identity, and serialized publication for one complete-family trial registration plus its exact qualification plan. |
| `policy_authoring.py` | Versioned policy registry validation, synchronization, conformance execution, immutable releases, and lifecycle evidence. |
| `legacy_experiments.py` | Module alias for the canonical legacy inventory guard. |
| `__init__.py` | Package marker; shared APIs are normally imported from their defining modules. |

### `src/trading/commands/`

CLI parser registration and handlers grouped by public responsibility.

| File | Purpose |
|---|---|
| `legacy.py` | Explicit `trading legacy ...` tree with read-only diagnostics and fail-closed retired operations. The former top-level aliases no longer exist. |
| `workflow.py` | Workflow authoring, validation, release, and study parser/handler. |
| `research.py` | Workflow-native definition listing, snapshot, run, and exact orchestration provenance. |

### `src/trading/legacy/`

Canonical read-only compatibility implementation for the retired experiment system. It owns the
registry implementation, archived-result diagnostics, definition resolution, retired evaluation and
analysis, archived documentation audit, freshness audit, and inventory guard. No module in this
package authorizes new research or result publication.

### `src/trading/workflow/`

Canonical workflow lifecycle implementation: authoring, studies, exact-study qualification,
terminal evidence, and qualification orchestration. Historical `trading.core.*` imports alias these
same module objects so monkeypatching and process-global state remain compatible.

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
| `migration_policy.py` | Scans experiment data access, enforces the zero-tolerance provider boundary, and retains typed allowlist compatibility primitives from the completed migration. |
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
| `paths.py` | Canonical categorized result-directory helpers plus append-only, SHA-256-bound historical path migration. It preserves v009 one-hop mappings and permits only one additional byte-identical v010 retirement hop. |
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
| `README.md` | Active definition-tree boundary, frozen-source compatibility, and new source-placement guidance. |
| `primitives/` | Destination for new reusable workflow-native definition seams; existing top-level seams remain at evidence-pinned paths. |
| `_template/` | Starting structure for a workflow-native definition. |
| `<family>/<trial>/definition.py` | Stable source entry point for one permanent workflow-governed trial identity. |

### `src/trading/experiments/`

This is the import facade for the closed legacy inventory.
Archived source packages live under repository-root `legacy/experiments/`, while the registry
extends its package search path in a repository checkout so their historical import identities remain
`trading.experiments.<experiment_name>`. It auto-imports every inventoried package whose name does
not start with `_`; each package's `__init__.py` registers its strategy. CI scans the archive and
rejects new or renamed identities. Registration supports read-only diagnostics, source inspection,
and fail-closed exits for pre-existing positions only; it does not authorize research execution or
publication. New formal research uses `src/trading/research_definitions/`.

| Pattern | Purpose |
|---|---|
| `src/trading/experiments/__init__.py` | Historical package-search facade that re-exports the canonical `trading.legacy.experiments` registry and discovers the physical archive. |
| `src/trading/experiments/README.md` | Local ownership warning: this directory is a closed compatibility facade and not a research extension point. |
| `legacy/experiment-overviews/EXPERIMENTS_<TICKER>.md` | Archived per-asset result tables, parameter comparisons, and machine-oriented `AI_CONTEXT`. |
| `legacy/templates/experiment/` | Former package template retained outside auto-discovery; it is not a supported starting point. |
| `legacy/experiments/<experiment_name>/config.py` | Experiment identity, ticker, periods, thresholds, exits, and other parameters. |
| `legacy/experiments/<experiment_name>/signal_detector.py` | Indicators and entry-signal logic. |
| `legacy/experiments/<experiment_name>/strategy.py` | Frozen historical strategy implementation retained for inspection, reproduction source, and exit compatibility; its former research hooks have no public execution authority. |
| `legacy/experiments/<experiment_name>/__init__.py` | Registers the strategy under its unchanged import identity for checkout-only compatibility. |

## Tests and repository checks

| Path | Purpose |
|---|---|
| `tests/README.md` | Placement contract for new tests and explanation of pinned root-level test exceptions. |
| `tests/conftest.py` | Shared pytest setup and fixtures. |
| `tests/test_*.py` | Tests whose historical paths or exact bytes are pinned by released policy or frozen workflow-study evidence; do not relocate them during organizational cleanup. |
| `tests/legacy/test_*.py` | Fast legacy import compatibility, archived diagnostics, and fail-closed CLI tests. |
| `tests/legacy/conformance/README.md` | Marker, execution-frequency, and closed-inventory maintenance contract for exhaustive legacy replay. |
| `tests/legacy/conformance/test_*_followup_snapshot_contract.py` | Complete primary and auxiliary legacy bundle/formal-offline matrix: 41 fixed smoke cases run in fast regression; remaining cases run only in full conformance. |
| `tests/workflow/test_*.py` | Workflow authoring, study, qualification, and terminal-evidence tests. |
| `tests/research/test_*.py` | Workflow-native definition, reproducibility, result-schema, run, and registry tests. |
| `tests/market_data/test_*.py` | Provider, cache, validation, coverage, bundle, and migration-boundary tests. |
| `tests/operations/test_*.py` | Ledger, current followup compatibility, qualification, sleeve, and drift operational tests. |
| `tests/policies/test_*.py` | Policy resolution, composition, definition-identity, and version-specific conformance tests. |
| `tests/repository_checks/test_*.py` | Contract tests for executable repository architecture and ownership checks. |
| `tests/workflow/README.md` | Declares `tests/workflow/` as the destination for new workflow lifecycle tests while pinned root tests stay in place. |
| `config/repository-checks/README.md` | Maintenance contract for active repository-wide checks and their tracked configuration. |
| `config/repository-checks/check_path_ownership.py` | Validates ownership schema, owners, path existence, unique coverage, and closed compatibility directories. |
| `config/repository-checks/path-ownership.json` | Executable projection of this document's public path statuses and canonical owners. |
| `config/repository-checks/check_experiment_market_data_access.py` | Zero-tolerance CI scanner that rejects experiment access bypassing the declared market-data boundary and runtime yfinance use outside the provider. |
| `config/repository-checks/check_legacy_experiment_inventory.py` | CI entry point that rejects additions or rename-based replacements in the legacy experiment tree. |
| `config/repository-checks/legacy-experiment-inventory.json` | Sorted stage-one baseline of frozen legacy experiment package identities; removals are allowed but additions are not. |

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
| `results/README.md` | Human-facing map from common research questions to the correct result namespace, filename semantics, authority boundary, read-only inspection commands, and safe cleanup rules. |
| `results/research-trials/<family>/<trial>/<artifact>` | Workflow-native trial snapshot manifests and formal results, grouped by exact family/trial source identity. |
| `results/migration-evidence/<experiment>/<artifact>` | Retained parity and migration-result envelopes; these never become current result authority. |
| `results/workflows/<workflow>--vNNN/<study>/<stage>/<artifact>` | Permanently retained tracked workflow-study Development gates, selections, challenge manifests, and distinct challenge evidence. |
| `results/evidence/research/<sha256>.md` | Permanently retained tracked content-addressed pre-freeze research evidence referenced by immutable candidate-freeze records. |
| `results/evidence/qualification/<sha256>.json` | Permanently retained tracked self-contained qualification registry/checkpoint snapshot replayed for terminal decisions and Development absence proofs. |
| `results/registries/trial_registry.json` | Tracked append-only experiment-family/trial inventory and formal observations. |
| `results/registries/path-migrations.json` | Tracked append-only old-to-new result path registry. Entries pin source/destination identities, artifact class, migration version, and SHA-256. A v009 path may have exactly one additional byte-identical v010 retirement hop; readers reject longer chains, cycles, missing terminal bytes, or digest drift. |

The legacy experiment result authority is retired. All of its last retained results and manifests
live under `legacy/results/`; `results/experiment-results/` must not exist or be recreated.
Comparison, explicit result-status commands, and the labeled legacy archive freshness audit may
inspect the archive. Active-knowledge freshness, evaluation/ranking, followup new entries,
Shadow/Active, qualification, formal evidence verification, and all writers reject archived
results. Historical frozen paths resolve only through
the bounded, digest-verified `results/registries/path-migrations.json`; released workflow and study
bytes are not rewritten. See `legacy/README.md` and `docs/legacy-experiment-retirement-v010.md`.

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
| Inspect or reproduce legacy source without publishing outcomes | Existing `legacy/experiments/<identity>/` | Preserve semantic identity and archived evidence; all public legacy execution and writer entry points remain retired. |
| Change legacy compatibility or diagnostics | `src/trading/legacy/` | Preserve `trading.experiments` and `trading.core.*` aliases, archived read-only boundaries, and legacy tests. |
| Add a new research identity | `src/trading/research_definitions/` | Released workflow/study, exact policy versions, immutable definition/data evidence, tests. Never add a legacy experiment package. |
| Add or revise reusable research constraints | `policies/` and `src/trading/policies/` | Conformance tests, affected workflow version, `docs/policies.md`, and technical docs. |
| Change shared strategy/backtest behavior | `src/trading/core/` | Focused tests, affected phase docs, and experiment docs if metrics or contracts change. |
| Change provider/cache behavior | `src/trading/market_data/` | `docs/market-data.md`, tests, ADR when architectural. |
| Change snapshots/results/formal runs | `src/trading/research_data/` | Reproducibility/result docs, tests, ADR when architectural. |
| Change CLI behavior | Matching `src/trading/commands/` module plus `src/trading/cli.py` dispatch when needed | `CLAUDE.md` commands, `README.md`, relevant contract docs, and CLI tests. |
| Change followup selection or reporting | `src/trading/followup.py` / `followup_backtest.py` | Followup tests and relevant experiment/result docs. |
| Change a repository workflow contract | `workflows/` | Use `trading-author-workflow`; generated indexes and release evidence must remain valid. |
| Change workflow runtime behavior | `src/trading/workflow/` | Preserve old core aliases, focused workflow tests, and pinned source/evidence paths. |
| Change repository layout or ownership | Affected paths | Update this document in the same change. |

Versioned Phase 6 workflow contracts live at
`docs/historical-qualification-and-shadow-vNNN.md`. Each file is an immutable normative dependency
for the workflow version that pins it; behavioral changes create a new document version instead of
rewriting a document pinned by a released workflow.
