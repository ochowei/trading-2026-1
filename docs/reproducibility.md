# Reproducibility Foundation

Phase 2 creates immutable evidence for market data and executable research definitions. Runtime
blobs live under `.research-data/blobs/` and remain outside Git. Result-linked manifests use the
`*.snapshot.json` suffix under `results/` so they remain trackable. A cache file is never accepted as
a substitute for a referenced blob.

## Data blobs and snapshot manifests

`ResearchDataStore` copies the exact canonical CSV bytes validated by Phase 1 and uses their SHA-256
digest as the blob identity and storage path. Publication requires `last_complete_refresh` to exist
and to be at least as recent as any incremental refresh. The cache cutoff must exactly match the
snapshot Signal Decision Time. A later incremental refresh makes that generation ineligible until
another full refresh completes.

Publication uses temporary files and a no-overwrite immutable link. Existing identical content is
shared; existing different or corrupted content raises `ImmutableBlobCorruptionError` and remains
untouched. Snapshot loading verifies manifest identity, schema, declared and actual cutoffs, byte
counts, row counts, SHA-256 digests, session coverage, and auxiliary availability policies before it
returns a defensive-copy `MarketDataBundle`. It never calls a provider or repairs evidence.

A manifest records every declared series with provider, symbol, interval, adjustment policy, role,
history start, availability policy, data cutoff, full-refresh timestamp, blob identity, and optional
definition reference. Its `snapshot_id` is the SHA-256 of canonical manifest content excluding the
identity field itself.

## Research-definition evidence

`ResearchDefinitionStore.capture` requires explicit strategy, detector, and backtester Python
sources. The semantic fingerprint hashes:

- canonical resolved configuration;
- normalized Python ASTs without formatting or comments;
- explicit execution-engine version;
- Python version and caller-declared relevant dependency versions.

The content-addressed definition blob additionally retains exact source text and automatically
discovers the common source repository's Git HEAD, branch, dirty status, relevant diff, and status.
Sources without reconstructable Git context fail closed. A formatting-only change can
therefore preserve the semantic fingerprint while producing a different exact definition blob;
outcome-relevant source, configuration, engine, or dependency changes alter the fingerprint.

## Formal execution modes

`ResearchRunCoordinator` verifies the complete snapshot before invoking a runner:

- `online` is the default formal mode, requires data and definition evidence for the latest completed
  XNYS session, writes a historical result, and atomically advances `latest.json`;
- `offline` explicitly accepts an older complete snapshot, persists only a historical result, and
  never advances `latest.json`;
- `ephemeral` returns diagnostics without writing result or registry state.

`trading run --snapshot MANIFEST` selects formal online mode; `--offline MANIFEST` selects formal
offline mode. Both require snapshot-aware `run_with_bundle` and `capture_research_definition` seams,
and bind the captured current exact definition reference to the manifest before execution.
Unmigrated persisted execution requires explicit `--legacy`; `--ephemeral` remains available because
it changes no persisted results. Full detector migration remains Phase 9.

## Portable bundles

Snapshot bundle export verifies and packages `manifest.json`, every referenced data blob, the
referenced definition blob, and an optional result JSON. Import rejects duplicate, missing, or
unexpected archive members; verifies every identity and size; refuses immutable collisions; then
publishes blobs and the requested result-linked manifest. Replaying the imported bundle uses only
the restored `MarketDataBundle`, so signals, trades, and metrics are independent of Yahoo availability.

## Garbage collection

`trading data gc` recursively discovers the complete retained-manifest set under `results/` by
default; repeated `--manifest-root` options declare alternative complete roots. It protects every
referenced data and definition blob, considers only unreferenced blobs older than the declared grace
period, and defaults to dry-run. A missing root or malformed retained manifest fails closed. Deletion
requires `--apply`. Normal research, trading, result rotation, export, import, and verification paths
never invoke GC.

Corrupted or missing referenced blobs make their snapshot unreproducible. They may be restored only
by importing identical content from a bundle; a current provider download can never impersonate the
historical evidence.
