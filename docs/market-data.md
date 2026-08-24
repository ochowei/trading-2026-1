# CSV Market-Data Foundation

Phase 1 routes the existing `DataFetcher` primary-ticker path through a validated, disposable CSV
cache. The cache improves reliability and avoids repeated downloads; it is not reproducibility
evidence and must never substitute for the immutable research snapshots implemented by Phase 2.

## Supported contract

- Provider: Yahoo Finance only.
- Interval: one day (`1d`) only.
- Adjustment: `auto_adjust=True`; canonical fields are `Date,Open,High,Low,Close,Volume`.
- Decision cutoff: the latest completed XNYS session after its actual close plus a conservative
  30-minute buffer, including scheduled early closes.
- Storage: `.cache/market-data/` with invalid artifacts moved to
  `.cache/market-data-quarantine/`.

`MarketDataSeries` is the identity boundary. Symbols are encoded as versioned URL-safe base64 so
provider symbols such as `^VIX`, `BRK-B`, `BTC-USD`, and Unicode symbols cannot escape or collide in
filesystem paths.

## Cache publication

Each series has one canonical CSV, one JSON metadata sidecar, and one per-series lock. The sidecar
records provider, original symbol, interval, adjustment policy, schema version, data cutoff, latest
incremental refresh, latest complete refresh, the observation coverage policy, and the SHA-256
checksum of the exact CSV bytes. Existing sidecars without the new field remain readable as the
default `xnys_sessions` policy.

Writers wait for the lock for a bounded interval, recheck the active generation after acquiring it, download
through the provider boundary, validate the complete candidate, write temporary files, and publish
with atomic file replacement. A second concurrent request therefore observes the published cache
instead of issuing a duplicate download, including when both callers requested an explicit
incremental refresh. A failed candidate never replaces an existing valid cache.

Normal access uses an incremental refresh with a five-session conservative overlap. A full refresh
downloads the provider's complete history through the requested completed-session cutoff and sets
`last_complete_refresh`. Corporate-action differences inside the incremental overlap replace that
overlap as one provider generation; conflicting duplicate dates inside either provider response or
the assembled candidate remain corruption.

Full refresh is the prerequisite for Phase 2 snapshot eligibility. Blob publication, manifests,
portable bundles, definition evidence, and replay are specified in
[reproducibility.md](reproducibility.md); the disposable cache itself never becomes evidence.
For workflow-native families that require multiple definitions to use one exact market-data
generation, the first `trading research snapshot` performs the full refresh and later snapshots at
the same cutoff use `--reuse-full-refresh`. Reuse performs no provider access; snapshot publication
still verifies full-refresh eligibility, coverage, and the exact primary cutoff before copying the
same canonical cache bytes into content-addressed evidence. The study must compare the resulting
data-blob identities and stop before ranking if a required common series differs.

When an authorized historical study needs a cutoff earlier than the monotonic active cache,
`trading research snapshot --cache-root <isolated-path>` performs that full refresh in an explicit
disposable cache namespace. Its quarantine root is the sibling path with `-quarantine` appended.
Later family snapshots must use the same `--cache-root` together with `--reuse-full-refresh` so they
remain provider-free and bind the identical generation. The cache path is operational only and
does not become evidence; immutable manifests still carry the exact data-blob identity.

## Validation and corruption

Before publication and on active-cache use, validation checks:

- all required columns, with non-NaN finite values;
- parseable, unique, strictly increasing normalized dates;
- `Low <= Open/Close <= High` and `Low <= High`;
- nonnegative volume;
- complete XNYS session coverage for requirements using `xnys_sessions`, rejecting both missing
  sessions and unexpected non-session dates;
- unique, ordered, valid observation dates for requirements using `provider_observations`, without
  inventing missing sessions;
- sidecar identity, schema, data cutoff, and CSV checksum.

Session expectations come from the version-locked `exchange-calendars` XNYS calendar rather than a
hand-maintained holiday list, so full-history refreshes account for emergency closures such as the
September 2001 shutdown as well as scheduled early closes.

The session calendar is owned by `CsvMarketDataCache` for XNYS-complete series. Sparse auxiliary
series declare `provider_observations` and are validated on their actual observation dates; their
availability policy still controls which observations can be used at each XNYS decision session.

An exact duplicate observation may be deduplicated. Conflicting duplicates and every other invalid
row are reported without row dropping. Invalid active CSV/metadata is quarantined as a diagnostic
artifact, followed by one full rebuild attempt. If the provider cannot supply a complete valid
replacement, access fails closed.

## Declared dependencies and availability

`MarketDataRequirement` declares the complete history, role, and observation coverage policy of
each primary or auxiliary series; primary requirements must use complete XNYS session coverage,
while an auxiliary may use sparse provider observations. `MarketDataDeclaration` is the complete
execution declaration and requires exactly one primary series. Bundle construction rejects duplicate
declarations and data that begins after the first required primary session, has gaps in expected
XNYS sessions, or (for XNYS-covered requirements) contains non-session rows. Sparse auxiliary data
is not padded to an inferred calendar; its `AvailabilityPolicy` determines the backward as-of
observation and maximum acceptable observation lag.
`MarketDataService.build_bundle` resolves
every declaration through the same provider/cache boundary before constructing the defensive-copy
bundle. An auxiliary requirement must include an `AvailabilityPolicy` with publication lag and
maximum observation lag; the maximum cannot be shorter than the publication lag. Unknown
publication timing requires at least one primary-session lag.

`align_auxiliary` computes each auxiliary observation's first available primary session and selects
only the latest observation available at each ordered `SignalDecisionTime`. `MarketDataBundle`
retains the declaration and decision-session sequence, applies that alignment during validated
construction, and exposes only the policy-aligned auxiliary view—not the raw same-session frame. It
never selects forward and fails when no eligible observation exists or the maximum lag is exceeded.
The default excess-lag behavior remains fail-closed for the entire bundle. A research definition
may instead preregister the explicit `mark_unavailable` mode. That mode preserves the backward-as-of
row and its actual lag for audit, adds `ObservationAvailable=false`, and requires the definition to
suppress every signal on that decision; it never treats an over-age observation as current. The
mode is outcome-relevant, is serialized in the immutable manifest, and cannot be enabled after
preregistration to repair a failed observation.
The bundle rejects missing or undeclared series and returns defensive copies so detector code cannot
mutate it.

Historical snapshot replay supplies the ordered decision sequence from the declared primary
history through the snapshot cutoff. Consequently, an auxiliary frame loaded from a
`ResearchDataStore` is a row-for-row as-of view for every primary decision session, rather than a
single latest auxiliary row. A lagged auxiliary must therefore include enough observations before
the first declared decision session; if its earliest decision cannot be satisfied, snapshot loading
fails closed instead of silently dropping that decision.
Complete provider refresh blobs may contain observations earlier than a manifest entry's declared
`history_start`. Replay exposes the primary frame only from its first declared XNYS session onward,
while an auxiliary raw frame may retain earlier observations needed to prove publication-lag
availability at that first decision. Earlier primary rows cannot enter the runner or be required to
match the aligned auxiliary decision sequence.

`SessionCalendar` and `MarketDataReader` protocols define the shared structural boundaries, while
`RefreshKind` is the single vocabulary for incremental and full publication paths.

Phase 1 supplies these common contracts but intentionally does not migrate the existing detector
fleet. Direct detector downloads are removed family-by-family in Phase 9 with snapshot-based parity
checks.

## Market-data access policy

`config/repository-checks/check_experiment_market_data_access.py` scans experiment Python ASTs for
direct yfinance imports/calls, dynamic imports, and known legacy DataFetcher/provider/cache paths.
The Phase 9 migration allowlist has been retired after reaching zero entries, so CI now runs the
scanner in permanent zero-tolerance mode: any experiment bypass fails the check. Runtime yfinance
imports are permitted only in `market_data/provider.py`; imports anywhere else under
`src/trading/` also fail the check.

## Operations

```bash
trading data status SPY
trading data refresh SPY --start 2020-01-01
trading data refresh SPY --full
trading data refresh SPY --end 2026-08-04
```

`data status` is read-only: it reports valid, stale, corrupt, missing, or busy state. For an existing
series it uses a bounded shared lock so it cannot observe a writer between the CSV and metadata
replace, but it never creates a missing lock file, quarantines an artifact, calls Yahoo, or refreshes
data. `data refresh` is the explicit state-changing operation. CLI `--end` is inclusive;
the compatibility `DataFetcher(end=...)` retains its historical yfinance-style exclusive end.
An explicit refresh cannot move an existing active cutoff backward. Full refresh always downloads
complete history, so `--full` rejects `--start` instead of silently treating a partial range as full.

The compatibility `DataFetcher` retains Yahoo's supported `period` vocabulary. Period selection is
applied only after retrieving a normalized cache frame; an unknown period fails before provider
access, and an explicit `start` continues to take precedence as it did in the previous implementation.
