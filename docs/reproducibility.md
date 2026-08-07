# Reproducibility Foundation

Phase 2 creates immutable evidence for market data and executable research definitions. Runtime
blobs live under `.research-data/blobs/` and remain outside Git. Result-linked manifests use the
`*.snapshot.json` suffix under `results/` so they remain trackable. A cache file is never accepted as
a substitute for a referenced blob.

## Data blobs and snapshot manifests

`ResearchDataStore` copies the exact canonical CSV bytes validated by Phase 1 and uses their SHA-256
digest as the blob identity and storage path. Publication requires `last_complete_refresh` to exist
and to be at least as recent as any incremental refresh. A primary cache cutoff must exactly match
the snapshot Signal Decision Time; an auxiliary cutoff may be earlier when its declared coverage
and availability policies prove that the latest usable observation is available by the decision.
A later incremental refresh makes that generation ineligible until another full refresh completes.

Publication uses temporary files and a no-overwrite immutable link. Existing identical content is
shared; existing different or corrupted content raises `ImmutableBlobCorruptionError` and remains
untouched. Snapshot loading verifies manifest identity, schema, declared and actual cutoffs, byte
counts, row counts, SHA-256 digests, each entry's declared session or provider-observation coverage,
and auxiliary availability policies before it returns a defensive-copy `MarketDataBundle`. It never
calls a provider or repairs evidence.

A manifest records every declared series with provider, symbol, interval, adjustment policy, role,
history start, availability policy, observation coverage policy, data cutoff, full-refresh timestamp,
blob identity, and optional definition reference. Default XNYS coverage remains omitted from the
canonical wire format for compatibility; sparse provider-observation entries carry an explicit policy.
Its `snapshot_id` is the SHA-256 of canonical manifest content excluding the identity field itself.
Every official publication path requires a `.snapshot.json` destination and strictly compares input
bytes with the canonical round-trip, rejecting unknown fields and alternate JSON representations.

## Research-definition evidence

`ResearchDefinitionStore.capture` requires explicit strategy, detector, and backtester Python
sources. The semantic fingerprint hashes:

- canonical resolved configuration;
- normalized Python ASTs without formatting or comments;
- explicit execution-engine version;
- preregistered base and adverse stress execution-cost policies;
- Python version and caller-declared relevant dependency versions.

The content-addressed definition blob additionally retains exact source text and automatically
discovers the common source repository's Git HEAD, branch, dirty status, relevant diff, and status.
Sources without reconstructable Git context fail closed. A formatting-only change can
therefore preserve the semantic fingerprint while producing a different exact definition blob;
outcome-relevant source, configuration, engine, or dependency changes alter the fingerprint.
Reporting-only functions are excluded only through an explicit per-source symbol declaration;
function names and prefixes are never used as evidence that code is outcome-independent. The
declaration is honored only for one unambiguous symbol that is not referenced outside its own
definition; uncertain dependencies remain semantic.

## Formal execution modes

`ResearchRunCoordinator` verifies the complete snapshot before invoking a runner:

- `online` is the default formal mode, requires data and definition evidence for the latest completed
  XNYS session, writes a historical result, and atomically advances `latest.json`;
- `offline` explicitly accepts an older complete snapshot, persists only a historical result, and
  never advances `latest.json`;
- `migration` requires a passing fixed-snapshot parity artifact and publishes only the immutable
  `results/<experiment>/<snapshot_id>.migration-result.json` envelope. It records a new trial
  observation as `migration-pending`, never advances `latest.json`, and never writes qualification
  or lifecycle state. Requalification must produce a separate current result;
- `ephemeral` returns diagnostics without writing result or registry state.

`trading data snapshot --experiment NAME` captures current definition evidence and defaults to
the immutable `results/NAME/<snapshot_id>.snapshot.json` path. `trading run NAME` selects formal
online mode by default by discovering the newest retained manifest whose exact definition reference
matches the current experiment. `--snapshot MANIFEST` overrides discovery and `--offline MANIFEST`
selects formal offline mode; pairing it with `--migration-parity ARTIFACT` selects migration mode.
Formal modes require snapshot-aware `run_with_bundle`,
`capture_research_definition`, and `declare_experiment_trial` seams, and bind the captured current
exact definition to the manifest before execution. A snapshot-aware experiment also exposes the
side-effect-free `market_data_requirements()` declaration; preparation and retained-snapshot
refresh use it verbatim and fail closed on declaration drift. Semantic fingerprints remain the
identity used for result validity and trial lineage.
The runner returns a typed `CanonicalSleeveInput`; the coordinator itself applies the frozen
definition's cost policies through the shared sleeve evaluator and publishes the resulting evidence.
Runner-supplied precomputed canonical evidence is not trusted.
Unmigrated persisted execution requires explicit `--legacy`; `--ephemeral` remains available because
it changes no persisted results. Full detector migration remains Phase 9.

Data-access migration parity executes the legacy-compatible and migrated paths against the same
verified bundle object. Indicator cells, ordered signal dates, and canonical trade payloads are
compared exactly. A passing comparison may be retained at
`results/<experiment>/<snapshot_id>.migration-parity.json`; the artifact records both definition
references, runtime/dependency identity, aggregate and per-layer checksums, deterministic
difference identities, corrections, and a self-verifying parity digest. The artifact is immutable,
and an unexplained difference remains a migration blocker.

The migration result envelope is deliberately not a normal result-schema document. It embeds the
schema-3 migrated output, the passing parity digest, and `requalification_required: true` under a
deterministic `<snapshot_id>.migration-result.json` name beside the parity artifact. Publication is
content-addressed and no-overwrite; a changed retry fails closed. The ordinary legacy result reader
continues to read existing legacy files, while latest-result and qualification readers cannot
mistake migration evidence for a current qualified result.

## Result validity and trial history

Current result schema version 3 retains the existing Part A / Part B / Part C payload while adding
the data snapshot identity, actual cutoff, definition snapshot identity, semantic definition
fingerprint, development summary, historical stability folds, shadow evidence, live evidence, and
legacy period results. It also requires canonical sleeve evidence with gross, base-net, and
stress-net daily-equity paths, explicit cost assumptions, raw candidates, and parity diagnostics.
The validity classifier derives one of `valid`, `data-stale`,
`definition-stale`, `unreproducible`, `legacy`, or `migration-pending` without mutating the result
or refreshing data.

`valid` requires a complete successful result whose immutable data and definition evidence can be
verified and whose data cutoff and semantic definition are current. Missing or corrupt blobs are
`unreproducible`; old files, including Phase 3 schema-v2 results without canonical sleeve evidence,
remain readable as `legacy` and are never assigned synthetic snapshot
identities. Failure to resolve the current definition also yields `unreproducible`, never `valid`.
An embedded migration-mode result is classified as `migration-pending` even when its evidence is
fresh; it is never qualifiable until a separately published, requalified result exists.
Comments, formatting, and safely declared reporting-only symbols are ignored by the semantic
fingerprint, while undeclared or behavior-affecting changes create a new definition lineage.

`latest.json` is advanced only by a successful formal online run. Formal offline runs write only
historical results, ephemeral runs write neither results nor registry observations, and the legacy
compatibility path writes historical legacy output only. Failed or partial formal attempts are
retained as failed observations; partial output is never published as a successful result.
If only latest-pointer publication fails after a complete run, its historical evidence remains and
the registry records both the successful execution and the separate publication failure.

`results/trial_registry.json` is append-only and keyed by experiment family plus semantic definition
fingerprint. Repeated runs of the same definition append observations; a new fingerprint creates a
new trial. Result deletion is represented by a tombstone, not erasure. Legacy experiments may be
explicitly inventoried with `uv run trading result registry seed`; that inventory is marked as
having incomplete selection history and is not ranking evidence.

Read-only status, comparison, and freshness commands never refresh or write results. Explicit asset
evaluation fully refreshes retained data requirements, publishes a new current exact snapshot,
reruns every stale candidate, and emits no partial ranking if any candidate is legacy,
unreproducible, or cannot be brought to a valid current state. Phase 3 does not migrate the existing
detector batch automatically; snapshot-aware seams and a prepared manifest are required for refresh.
Followup qualification and experiment-documentation workflows apply the same computed-validity
gate before consuming result metrics.

Formal asset ranking reads only the base-net Sharpe calculated from canonical daily sleeve equity;
legacy Part B independently compounded metrics are never a fallback. See
[canonical-sleeve-execution.md](canonical-sleeve-execution.md) for the capital, event-order, cost,
and parity contract.

See [result-validity-and-trial-history.md](result-validity-and-trial-history.md) for the complete
field and publication contract.

## Portable bundles

Snapshot bundle export verifies and packages `manifest.json`, every referenced data blob, the
referenced definition blob, and an optional result JSON. Import rejects duplicate, missing, or
unexpected archive members; verifies every identity, size, adjusted-daily schema, session coverage,
and exact canonical CSV serialization; refuses immutable collisions; then publishes blobs and the
requested result-linked manifest. Replaying the imported bundle uses only
the restored `MarketDataBundle`, so signals, trades, and metrics are independent of Yahoo availability.

## Garbage collection

`trading data gc` recursively discovers the complete retained-manifest set under `results/` by
default; repeated `--manifest-root` options add archive roots without removing the default. It protects every
referenced data and definition blob, considers only unreferenced blobs older than the declared grace
period, and defaults to dry-run. A missing root or malformed retained manifest fails closed. Deletion
requires `--apply`. Normal research, trading, result rotation, export, import, and verification paths
never invoke GC.

Corrupted or missing referenced blobs make their snapshot unreproducible. They may be restored only
by importing identical content from a bundle; a current provider download can never impersonate the
historical evidence.
