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
incremental refresh, latest complete refresh, and the SHA-256 checksum of the exact CSV bytes.

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

## Validation and corruption

Before publication and on active-cache use, validation checks:

- all required columns, with non-NaN finite values;
- parseable, unique, strictly increasing normalized dates;
- `Low <= Open/Close <= High` and `Low <= High`;
- nonnegative volume;
- exact primary US session coverage between the series' first and last observation, rejecting both
  missing sessions and unexpected non-session dates;
- sidecar identity, schema, data cutoff, and CSV checksum.

Session expectations come from the version-locked `exchange-calendars` XNYS calendar rather than a
hand-maintained holiday list, so full-history refreshes account for emergency closures such as the
September 2001 shutdown as well as scheduled early closes.

The session calendar is owned by `CsvMarketDataCache`; coverage is therefore mandatory for every
public publish and load rather than an optional validation argument supplied by callers.

An exact duplicate observation may be deduplicated. Conflicting duplicates and every other invalid
row are reported without row dropping. Invalid active CSV/metadata is quarantined as a diagnostic
artifact, followed by one full rebuild attempt. If the provider cannot supply a complete valid
replacement, access fails closed.

## Declared dependencies and availability

`MarketDataRequirement` declares the complete history and role of each primary or auxiliary series.
Bundle construction rejects duplicate declarations and data that begins after the first required
primary session, has gaps in expected XNYS sessions, or contains non-session rows.
`MarketDataService.build_bundle` resolves
every declaration through the same provider/cache boundary before constructing the defensive-copy
bundle. An auxiliary requirement must include an `AvailabilityPolicy` with publication lag and
maximum observation lag; the maximum cannot be shorter than the publication lag. Unknown
publication timing requires at least one primary-session lag.

`align_auxiliary` computes each auxiliary observation's first available primary session and selects
only the latest observation available at a `SignalDecisionTime`. `MarketDataBundle` retains the
declarations and decision time, applies that alignment during validated construction, and exposes
only the policy-aligned auxiliary view—not the raw same-session frame. It never selects forward and
fails when no eligible observation exists or the maximum lag is exceeded. The bundle rejects
missing or undeclared series and returns defensive copies so detector code cannot mutate it.

`SessionCalendar` and `MarketDataReader` protocols define the shared structural boundaries, while
`RefreshKind` is the single vocabulary for incremental and full publication paths.

Phase 1 supplies these common contracts but intentionally does not migrate the existing detector
fleet. Direct detector downloads are removed family-by-family in Phase 9 with snapshot-based parity
checks.

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
