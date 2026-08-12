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

## Agent and automation configuration

### `.agents/`

Repository-owned Agent knowledge and skills.

| Path | Purpose |
|---|---|
| `.agents/context/cross_asset_lessons.md` | Compact cross-asset lessons, prohibited directions, parameter-scaling guidance, and freshness metadata. |
| `.agents/context/cross_asset_evidence.md` | Detailed evidence supporting the compact cross-asset lessons. |
| `.agents/rules/execution-model.md` | Mandatory execution-model contract for non-grandfathered experiments. |
| `.agents/skills/trading-*/SKILL.md` | Workflow instructions for a specific repository research task. |
| `.agents/skills/trading-*/agents/openai.yaml` | Skill discovery metadata and default Agent presentation. |
| `.agents/skills/trading-*/assets/` | Templates copied or adapted by a skill, currently used by workflow authoring. |
| `.agents/skills/trading-*/references/` | Detailed contracts loaded by a skill only when its workflow needs them. |

### `.claude/commands/`

Compatibility command definitions for the experiment lifecycle. Files such as
`new-experiment.md`, `run-experiment.md`, and `evaluate-best.md` route older Claude command flows to
the corresponding repository behavior. New cross-Agent workflows should normally live in
`.agents/skills/trading-*/`.

### `.github/workflows/`

| Path | Purpose |
|---|---|
| `.github/workflows/lint.yml` | Runs Ruff lint and formatting checks in CI. |
| `.github/workflows/tqqq-backtest.yml` | Manually dispatches supported experiment backtests; its experiment choices must stay synchronized with experiment additions required by `CLAUDE.md`. |
| `.github/workflows/trading-followup-summary.yml` | Produces the scheduled/manual followup summary automation. |

## Documentation

### `docs/`

| Path | Purpose |
|---|---|
| `docs/ARCHITECTURE.md` | This canonical repository map and file-ownership guide. |
| `docs/market-data.md` | CSV market-data provider, cache, validation, freshness, and CLI contract. |
| `docs/reproducibility.md` | Immutable blobs, manifests, definitions, bundles, run modes, and garbage collection. |
| `docs/result-validity-and-trial-history.md` | Result schemas, validity states, evaluation boundaries, and append-only trial history. |
| `docs/canonical-sleeve-execution.md` | Canonical sleeve capital, execution-cost scenarios, metrics, and parity evidence. |
| `docs/manual-execution-ledger.md` | Manual ledger domain, integrity, broker reconciliation, and CLI contract. |
| `docs/historical-qualification-and-shadow.md` | Historical folds, benchmark gates, prospective Shadow evidence, and qualification lifecycle. |
| `docs/controlled-followup-cutover.md` | Followup lifecycle, authorization, parity, rollback, and allocation epochs. |
| `docs/live-drift-and-recovery.md` | Frozen drift envelopes, health states, hard guards, checkpoints, and recovery. |
| `docs/phase-9-primary-followup-migration.md` | Primary followup migration boundaries, parity evidence, and verification. |
| `docs/strategy-forward-replication-research-workflow.md` | Human-readable design of the strategy replication and promotion research workflow. |
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
| `src/trading/cli.py` | Unified command parser and dispatcher for experiments, results, data, ledger, qualification, followup lifecycle, drift, and versioned workflows. |
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
| `qualification_workflow.py` | Forward Selection Epoch registration and historical-screen orchestration. |
| `workflow_authoring.py` | Versioned workflow metadata, hashing, indexes, releases, and lifecycle transitions. |
| `workflow_studies.py` | Study scaffolding, preregistration, stage transitions, evidence, and completion. |
| `__init__.py` | Package marker; shared APIs are normally imported from their defining modules. |

### `src/trading/market_data/`

Fail-closed boundary around Yahoo adjusted daily OHLCV and the validated local cache.

| File | Purpose |
|---|---|
| `contracts.py` | Calendar/reader protocols and refresh vocabulary. |
| `models.py` | Market series, requirements, availability policies, decisions, and metadata values. |
| `provider.py` | Provider protocol and Yahoo Finance adapter. |
| `calendar.py` | XNYS sessions, historical special closures, and actual-close cutoffs. |
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
| `models.py` | Typed blob, manifest, definition, run, and garbage-collection values. |
| `manifest_codec.py` | Strict canonical manifest encoding and snapshot identity. |
| `store.py` | Snapshot publication, verification, portable bundles, references, and garbage collection. |
| `definitions.py` | Semantic fingerprints and exact-source definition blobs, including dirty-worktree capture. |
| `result_schema.py` | Versioned result payloads, computed validity, and legacy compatibility. |
| `runs.py` | Online, offline, migration, and ephemeral run/publication boundaries. |
| `migration.py` | Immutable parity-linked migration-result publication. |
| `parity.py` | Fixed-snapshot parity evidence and immutable parity artifacts. |
| `trial_registry.py` | Append-only experiment trial identities, observations, and tombstones. |
| `qualification_registry.py` | Local append-only Historical and Shadow lifecycle evidence. |
| `__init__.py` | Curated public research-data API exports. |

### `src/trading/experiments/`

The experiment registry auto-imports every package whose name does not start with `_`; each
package's `__init__.py` registers its strategy. No central registration list is required.

| Pattern | Purpose |
|---|---|
| `src/trading/experiments/__init__.py` | Registry, registration decorator, lookup/list APIs, and `pkgutil` auto-discovery. |
| `src/trading/experiments/_template/` | Starting structure for a new experiment. |
| `src/trading/experiments/EXPERIMENTS_<TICKER>.md` | Per-asset experiment overview, result table, parameter comparison, and machine-oriented `AI_CONTEXT`. |
| `src/trading/experiments/<experiment_name>/config.py` | Experiment identity, ticker, periods, thresholds, exits, and other parameters. |
| `src/trading/experiments/<experiment_name>/signal_detector.py` | Indicators and entry-signal logic. |
| `src/trading/experiments/<experiment_name>/strategy.py` | Connects config, detector, data declarations, execution, and formal research hooks. |
| `src/trading/experiments/<experiment_name>/__init__.py` | Registers the strategy under its CLI experiment name. |

## Tests and repository checks

| Path | Purpose |
|---|---|
| `tests/conftest.py` | Shared pytest setup and fixtures. |
| `tests/test_*.py` | Behavioral and contract tests, generally named after the module or lifecycle being protected. Snapshot-contract tests pin migration behavior for selected experiments. |
| `tools/check_experiment_market_data_access.py` | CI scanner that detects experiment access which bypasses the declared market-data boundary. |
| `ci/market-data-bypass-allowlist.json` | Typed, shrinking baseline of legacy experiment bypasses permitted during migration. |

Tests may contain explicit synthetic broker fixtures. Real broker exports, credentials, and personal
trading data must never be placed in `tests/` or committed anywhere.

## Research results and workflow registry

### `results/`

| Pattern | Purpose |
|---|---|
| `results/<experiment_name>/latest.json` | Retained latest result consumed by comparison, validity, documentation, and selection workflows. |
| `results/<experiment_name>/prev_1.json`, `prev_2.json` | Retained recent predecessors when present. |
| `results/<experiment_name>/<snapshot_id>.snapshot.json` | Retained immutable snapshot manifest used for reproducible formal execution. |
| `results/<experiment_name>/<timestamp>.json` | Historical run output; most such files are ignored unless explicitly retained by repository policy. |
| `results/trial_registry.json` | Tracked append-only experiment-family/trial inventory and formal observations. |

Never treat `latest.json` as valid solely because it exists; validity is recomputed against its data
and semantic definition references.

### `workflows/`

Versioned, tracked research-workflow registry shared by humans and Agents.

| Pattern | Purpose |
|---|---|
| `workflows/README.md` | Version lifecycle authority and generated registry index. |
| `workflows/<slug>--vNNN/README.md` | Version metadata, state, checksums, release evidence, and generated study/change indexes. |
| `workflows/<slug>--vNNN/WORKFLOW.md` | Self-contained workflow contract pinned by studies. |
| `workflows/<slug>--vNNN/studies/<study>/` | Preregistered plan, metadata, evidence, conclusion, and outcome for a workflow study when present. |
| `workflows/<slug>--vNNN/changes/<change>/` | Proposed workflow change, impact, decision, and validation evidence when present. |

Workflow metadata and generated indexes must be changed through the authoring/study services or
their repository skills, not hand-edited casually.

## Local-only runtime directories

These paths are intentionally ignored and must not be committed. Their absence in a fresh clone is
normal.

| Path | Purpose |
|---|---|
| `.venv/` | Local `uv` Python environment. |
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
| Add or revise a strategy experiment | `src/trading/experiments/` | Per-asset `EXPERIMENTS_<TICKER>.md`, required CI choices, tests, and result evidence. |
| Change shared strategy/backtest behavior | `src/trading/core/` | Focused tests, affected phase docs, and experiment docs if metrics or contracts change. |
| Change provider/cache behavior | `src/trading/market_data/` | `docs/market-data.md`, tests, ADR when architectural. |
| Change snapshots/results/formal runs | `src/trading/research_data/` | Reproducibility/result docs, tests, ADR when architectural. |
| Change CLI behavior | `src/trading/cli.py` | `CLAUDE.md` commands, `README.md`, relevant contract docs, and CLI tests. |
| Change followup selection or reporting | `src/trading/followup.py` / `followup_backtest.py` | Followup tests and relevant experiment/result docs. |
| Change a repository workflow contract | `workflows/` | Use `trading-author-workflow`; generated indexes and release evidence must remain valid. |
| Change repository layout or ownership | Affected paths | Update this document in the same change. |
