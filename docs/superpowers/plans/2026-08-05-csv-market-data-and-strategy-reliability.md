# CSV Market Data and Strategy Reliability Implementation Plan

**Status:** Accepted design baseline

**Decision date:** 2026-08-05

**Domain language:** [CONTEXT.md](../../../CONTEXT.md)

**Architecture decisions:** [docs/adr](../../adr)

## Objective

Replace repeated and hidden market-data downloads with a validated CSV-backed data layer, make persisted research reproducible and freshness-aware, align experiment ranking with the capital-constrained followup execution model, and introduce prospective qualification plus live risk controls before strategies can create new manual Firstrade positions.

The rollout must preserve historical evidence, avoid silently changing existing results, and introduce no new live-trading risk before the controlled cutover phase.

## Non-goals for the first version

- No SQLite, Parquet, Git LFS, cloud object storage, or broker API integration.
- No intraday, raw-price, or non-Yahoo market-data support.
- No volatility-weighted production allocation; it remains a separately evaluated future policy.
- No pyramiding or multiple active strategies for one ticker.
- No automatic modification of files under `pm/`.
- No attempt to relabel previously inspected Part A/B/C data as prospective evidence.

## Runtime storage boundaries

Runtime paths are local and excluded from normal Git tracking:

```text
.cache/market-data/              # Disposable current Yahoo adjusted daily-bar CSV cache
.cache/market-data-quarantine/   # Invalid cache artifacts retained for diagnosis
.research-data/blobs/            # Protected content-addressed data and definition blobs
state/manual-execution-ledger.csv
state/                            # Local proposal, projection, backup, and reconciliation state
```

Tracked repository artifacts include:

```text
CONTEXT.md
docs/adr/
results/<experiment>/latest.json
results/<experiment>/<timestamp>.json
result-linked snapshot manifests
experiment trial registry
```

Snapshot bundles are the portable unit for transferring exact market data, definition content, manifests, and results between machines.

## Cross-cutting safety rules

1. A trading-facing operation fails closed for stale, invalid, missing, or unreconciled inputs.
2. Existing confirmed positions continue to receive exit-management instructions during migration.
3. No persisted result is overwritten by an offline, ephemeral, failed, or partial run.
4. No detector may gain a new direct yfinance dependency.
5. Cache files may be rebuilt; immutable blobs may only be restored from identical content.
6. Every result-changing phase includes a schema migration path and legacy read support.
7. Network-dependent behavior is covered by provider fakes in automated tests; unit tests do not require Yahoo availability.
8. Code and relevant documentation are updated together under `CLAUDE.md` rules.

## Phase 1 — CSV market-data foundation

### Scope

Introduce a provider boundary for Yahoo Finance adjusted daily bars while preserving the current `DataFetcher` call surface where practical.

### Work

- Add immutable value types for:
  - market-data series identity;
  - market-data requirement;
  - signal decision time;
  - availability policy;
  - cache metadata and validation outcome.
- Implement a filesystem-safe ticker encoding that round-trips symbols such as `^VIX`, `BRK-B`, and `BTC-USD`.
- Store one canonical CSV per series with:
  - date;
  - Open, High, Low, Close, Volume;
  - deterministic column ordering and serialization.
- Store sidecar metadata containing:
  - provider;
  - symbol;
  - interval;
  - adjustment policy;
  - schema version;
  - data cutoff;
  - last incremental refresh;
  - last complete refresh;
  - content checksum.
- Validate unique ordered dates, required values, OHLC relationships, nonnegative volume, and expected primary-session coverage.
- Quarantine invalid caches and attempt a full redownload; fail closed when replacement is unavailable.
- Implement per-series filesystem locking, bounded waits, temporary-file writes, validation, and atomic replacement.
- Implement two refresh paths:
  - incremental refresh with a conservative overlap for daily followup;
  - full historical refresh before data becomes snapshot-eligible.
- Use the primary US trading session as the decision cutoff.
- Implement backward as-of auxiliary alignment with declared maximum observation lag and conservative publication lag.
- Add read-only `MarketDataBundle` construction.
- Add CLI diagnostics such as `trading data status` and explicit refresh support.
- Add `.cache/`, `.research-data/`, and `state/` runtime rules to `.gitignore` without ignoring manifests or tracked result metadata.

### Acceptance gate

- A second request for the same fresh series performs no network download.
- An incremental refresh requests only the missing and overlap period.
- Concurrent requests publish one valid CSV and do not duplicate the final download.
- Invalid or conflicting rows never enter the active cache.
- Auxiliary alignment never reads an observation published after signal decision time.
- Existing main-ticker callers receive equivalent normalized DataFrames.
- Ruff and all market-data unit tests pass.

## Phase 2 — Reproducibility foundation

### Scope

Create shared, immutable evidence for market data and executable research definitions.

### Work

- Define canonical bytes for adjusted daily-bar CSV blobs and calculate SHA-256 identities.
- Publish data blobs only from fully refreshed, snapshot-eligible series.
- Build snapshot manifests containing every primary and auxiliary series, availability policy, cutoff, checksum, and provider context.
- Build semantic research-definition fingerprints from:
  - canonical resolved config;
  - normalized Python AST for outcome-relevant strategy, detector, and backtester definitions;
  - explicit execution-engine version;
  - Python and relevant dependency versions.
- Store content-addressed definition blobs, including relevant uncommitted source content and Git context.
- Add formal execution modes:
  - default online persisted run;
  - explicit `--offline` persisted run using an older complete snapshot;
  - explicit `--ephemeral` run that changes no result or registry state.
- Add snapshot-bundle export, import, verification, and collision checks.
- Add reference-aware garbage collection:
  - dry-run by default;
  - explicit apply option;
  - grace period;
  - no deletion of referenced blobs.
- Add result replay tests that use exported bundles without network access.

### Acceptance gate

- Two experiments using identical bytes share one data blob.
- Changing comments or formatting does not change the semantic fingerprint.
- Changing a signal threshold, execution rule, or relevant dependency identity does change it.
- A dirty-worktree formal run can be reconstructed from its definition snapshot.
- An offline run never advances `latest.json`.
- A corrupted blob makes the result unreproducible and is never replaced with new provider data.
- Export/import followed by replay yields identical signals, trades, and metrics.

## Phase 3 — Result validity and trial history

### Scope

Make result status explicit and retain the full formal search history.

### Work

- Introduce a versioned result schema with:
  - validity status;
  - data and definition snapshot identities;
  - data cutoff;
  - definition fingerprint;
  - development summary;
  - historical stability folds;
  - shadow evidence;
  - live evidence;
  - legacy Part A/B/C results when present.
- Keep old result files readable and mark them as legacy rather than synthesizing missing snapshots.
- Publish `latest.json` only from a complete, fresh, current-definition online run.
- Add status values for valid, data-stale, definition-stale, and unreproducible results.
- Make command behavior explicit:
  - `compare` displays status and remains read-only;
  - `freshness` reports only;
  - `sync-docs` rejects stale sources;
  - asset evaluation refreshes all stale candidates before ranking.
- Add an append-only experiment trial registry keyed by semantic definition fingerprint and experiment family.
- Record failed and removed formal trials permanently.
- Treat later observations of the same definition as observations, not new trials.
- Seed legacy entries from discoverable experiments and mark their selection history incomplete where exact variants cannot be reconstructed.
- Add `trading result status` or equivalent diagnostics.

### Acceptance gate

- Source or config changes invalidate only dependent results.
- Non-behavioral reporting changes do not mass-invalidate experiments.
- Partial candidate refresh cannot produce a complete ranking.
- Deleted experiment code does not erase registered trial history.
- Legacy files remain inspectable but cannot grant new qualification.
- No stale result can update experiment documentation or followup qualification.

## Phase 4 — Canonical strategy-sleeve execution

### Scope

Use one capital-constrained execution path for experiment evaluation and followup simulation.

### Work

- Extract or replace the current followup sleeve simulation with a canonical reusable sleeve engine.
- Enforce one open position per strategy sleeve.
- Record overlapping signals as skipped with reason `position_already_open`.
- Use normalized initial sleeve capital and fractional quantities.
- Prevent borrowing, cross-sleeve transfer, and intra-epoch rebalancing.
- Produce daily cash, position value, equity, utilization, and drawdown.
- Calculate ranking metrics from daily sleeve equity rather than independently compounded signal returns.
- Preserve raw signal and candidate-trade diagnostics separately.
- Apply one preregistered execution cost policy consistently.
- Run gross, base-net, and stress-net scenarios.
- Build parity reports comparing old and canonical paths at signal and trade level.

### Acceptance gate

- Research evaluation and followup-backtest use the same sleeve engine.
- Overlapping signals cannot increase simulated capital exposure.
- Ranking metrics reproduce daily-equity calculations independently in tests.
- Base and stress execution assumptions are present in result fingerprints.
- Every intentional difference from legacy Part A/B/C results is classified and documented.

## Phase 5 — Manual trading state and idempotent proposals

### Scope

Stop inferring actual positions from backtests and establish a local, auditable manual-execution authority.

### Work

- Add explicit ledger initialization with:
  - managed capital;
  - followup universe;
  - initial equal sleeve capital;
  - first allocation epoch.
- Implement append-only CSV execution events for submission, fill, partial fill, cancellation, fee, deposit, withdrawal, manual adjustment, and correction.
- Link each event through a hash chain and verify accounting invariants on replay.
- Derive disposable position, cash, and cost-basis views from ledger replay.
- Add ledger CLI operations for init, verify, record, reconcile, export, and import.
- Add stable deterministic proposal IDs.
- Prevent repeated followup runs from producing duplicate actionable proposals.
- Link confirmed fills to proposals; classify unrelated manual trading separately.
- Detect changed terms for an existing proposal as a conflict.
- Base stop, target, expiry, and quantity instructions only on actual positions and sleeve cash.
- Block new entries on ledger integrity or broker-reconciliation failure.
- Run the entire phase in dry-run mode before live cutover.

### Acceptance gate

- Ledger replay deterministically reconstructs positions and cash.
- Editing or deleting an old event is detected before followup produces a new BUY.
- Corrections work only through new events.
- Repeated identical followup runs return the same proposal IDs.
- An unconfirmed proposal never creates an actual position.
- Manual fill prices and quantities drive subsequent exit instructions.
- Ledger files and credentials never enter Git.

## Phase 6 — Historical qualification and prospective Shadow

### Scope

Replace fixed Part A/B/C qualification with an explicit lifecycle and multiple-testing-aware evidence.

### Work

- Implement the Historical Stability Screen:
  - at least three development years;
  - at least five non-overlapping annual evaluation folds;
  - signal-date fold attribution and complete exit tracking;
  - purge/embargo matching holding and execution dependencies.
- Enforce historical gates:
  - at least twenty completed trades;
  - at least three traded folds;
  - at least sixty percent positive traded folds;
  - positive aggregate cumulative return;
  - aggregate profit factor above 1.1;
  - no stress-drawdown breach;
  - no fold above fifty percent of profits or trades.
- Add three benchmark layers:
  - cash;
  - preregistered family baseline;
  - exposure-matched random entry.
- Add family-wise block-bootstrap selection adjustment with at least 90 percent adjusted confidence.
- Freeze qualified research definitions before prospective observation.
- Start prospective evidence only from formal registration time; never backfill from legacy Part C.
- Implement Shadow paper proposals and canonical simulated fills.
- Require at least 252 completed sessions and twelve completed shadow trades before activation evaluation.
- Require positive prospective cumulative return, profit factor above one, stress-limit compliance, and no critical drift.
- Restart Shadow evidence after any outcome-relevant definition change.

### Acceptance gate

- No historical-only result can become Active.
- No trade appears in more than one qualification fold.
- Zero-signal folds remain visible.
- Multiple-testing adjustment includes every registered family trial.
- Checkpoint dates and thresholds are frozen before outcomes are known.
- Low-frequency strategies remain Shadow when evidence is insufficient.

## Phase 7 — Controlled followup cutover

### Scope

Move current followup operation to the new data, execution, ledger, and qualification contracts without abandoning open positions.

### Work

- Initialize the manual ledger from a user-verified broker reconciliation.
- Mark every current followup strategy Legacy Active.
- Continue existing confirmed-position exit management.
- Pause all new entry proposals at cutover.
- Migrate current followup strategies and all their auxiliary data dependencies before other legacy detectors.
- Run data-access migration parity against identical snapshots.
- Apply the Historical Stability Screen and register passing definitions as Shadow.
- Report each ticker as:
  - legacy position management;
  - migration pending;
  - historical screen failed;
  - Shadow;
  - insufficient evidence;
  - Active after prospective qualification.
- Enforce one Active Strategy per ticker.
- When replacing a strategy, keep the old one Retiring until its actual position is flat.
- Introduce allocation epochs for explicit universe or sleeve-capital changes.

### Acceptance gate

- No new BUY can originate from a Legacy Active, Retiring, Shadow, Paused, stale, or unreconciled strategy.
- Existing position instructions match verified ledger state.
- Every actionable order links to an Active Strategy, valid result, fresh data bundle, verified ledger, and stable proposal ID.
- Cutover can be rolled back to no-new-entry mode without losing ledger history or existing-position management.

## Phase 8 — Live drift and recovery

### Scope

Monitor Active strategies with frozen expectations and stop new risk when evidence departs materially.

### Work

- Freeze predictive drift envelopes before activation using historical folds plus Shadow evidence.
- Monitor:
  - performance drift;
  - signal drift;
  - execution drift from confirmed fills;
  - portfolio utilization and concentration drift.
- Implement Healthy, Watch, and Paused states.
- Apply immediate hard guards for data, ledger, reconciliation, execution, or stress-risk breaches.
- Move a strategy to Watch in the adverse twenty percent of its predictive envelope.
- Pause at the adverse five percent or after persistent Watch at two fixed checkpoints.
- Continue paper execution while Paused.
- Require normal recovery evidence of:
  - at least 126 later sessions;
  - at least six completed shadow trades;
  - cleared hard guards;
  - two scheduled checkpoints in the normal envelope.
- Allow data- or ledger-only pauses to recover after reconciliation and two clean checks without strategy-trade evidence.
- Treat any strategy-definition change as a new trial requiring full requalification.

### Acceptance gate

- A hard guard blocks new BUY proposals immediately.
- A Paused strategy continues managing existing positions.
- Drift thresholds cannot change after activation.
- Ordinary single losses inside the predictive envelope do not cause arbitrary pauses.
- Recovery cannot occur through a manual state edit or parameter change.

## Phase 9 — Complete experiment data-access migration

### Scope

Remove every remaining direct yfinance call from experiment implementations.

### Work

- Add CI enforcement that forbids new direct yfinance access immediately.
- Create the initial legacy allowlist from the current direct-download files.
- Migrate by asset or experiment family.
- Require each experiment to declare primary and auxiliary market-data requirements.
- Route every request through the shared provider and read-only bundle.
- Compare indicators, signal dates, fills, and trades on an identical snapshot.
- Document every non-parity correction.
- Make the allowlist monotonically shrink.
- Remove the compatibility layer and switch CI to a zero-tolerance rule when empty.

### Acceptance gate

- `src/trading/experiments/` contains no direct yfinance import or call.
- All experiment snapshots include every used market-data series.
- Offline replay performs no network access.
- The legacy allowlist and compatibility adapter are removed.

## Required test layers

### Unit tests

- CSV serialization, symbol encoding, metadata, validation, quarantine, locks, and atomic publish.
- Availability policies and as-of alignment.
- Blob identity, manifest references, bundle verification, and GC reachability.
- Semantic fingerprints and dependency invalidation.
- Sleeve state transitions and daily equity accounting.
- Ledger hash chain, corrections, replay, and reconciliation.
- Proposal IDs and idempotency.
- Fold construction, purge/embargo, concentration, benchmarks, and bootstrap determinism.
- Lifecycle, drift, hard-guard, activation, pause, and recovery transitions.

### Integration tests

- Online refresh followed by cache-only reuse.
- Full refresh to persisted result and exact offline replay.
- Stale result detection after data and definition changes.
- Formal, offline, and ephemeral run publication behavior.
- Trial registration across parameter changes and later observations.
- Followup from fresh data through proposal, fill, position management, and exit.
- Controlled cutover with legacy open positions.
- Detector migration parity using fixed snapshots.

### Acceptance tests

- CLI commands produce explicit data cutoff, definition identity, validity, lifecycle, and reconciliation status.
- No state-changing command hides partial failure.
- No read-only command triggers network or result writes.
- No live-facing command produces an actionable new entry from stale or unverified state.

## Documentation obligations

Every implementation phase updates the relevant architecture and commands in `CLAUDE.md`, user-facing behavior in `README.md`, and experiment documentation when observable strategy results change. Files under `pm/` remain untouched unless the user explicitly designates a future task as `HUMAN_PM_HELPER`.

## Final definition of done

The migration is complete only when:

1. Repeated market-data access is served from validated CSV cache with incremental updates.
2. Every decision-grade result is reproducible from data and definition snapshots.
3. Result consumers distinguish latest, valid, stale, incompatible, and unreproducible states.
4. Ranking and followup use the same capital-constrained sleeve execution.
5. Actual positions come only from a verified manual execution ledger.
6. Historical evidence can grant Shadow but not Active status.
7. Active status requires the accepted prospective evidence thresholds.
8. Live hard guards, drift, pause, and recovery are operational.
9. Existing followup strategies have been reclassified without abandoning confirmed positions.
10. No experiment detector can access yfinance directly.
