# Manual execution ledger

Phase 5 makes the local manual-execution ledger the authority for actual followup positions. It is
deliberately dry-run only: there is no broker API or automatic order submission.

## Domain model

`trading ledger init` writes the first canonical CSV event. Its metadata freezes the managed capital,
sorted followup universe, equal sleeve capital, any sub-quantum reserve cash, currency, and the first
allocation epoch. The initial sleeve amount is rounded down to eight decimal places; a remainder is
kept in the unallocated reserve so the accounting identity remains exact.

The CSV is append-only and hash chained. Every row has a contiguous sequence, canonical UTC timestamp,
previous hash, and event hash. Supported event types are:

- `submission`, `fill`, `partial_fill`, and `cancellation` for proposal lifecycle;
- `fee`, `deposit`, and `withdrawal` for cash movements;
- `manual_adjustment` for explicitly classified managed corrections or unrelated manual trades;
- `allocation_epoch` for an explicit flat-ledger universe and sleeve-capital reassignment;
- `correction`, which contains a replacement payload but never edits its target row.

Replay uses `Decimal` values only. Submissions do not change cash or positions. Confirmed fills must
reference a submitted proposal and are the only normal source of positions. Partial fills accumulate
against the submitted quantity, average fill price is retained separately from fee-inclusive cost
basis, and a sleeve cannot pyramid into a second position. `disposable_positions`,
`sleeve_cash`, and `cost_basis_by_position` are disposable projections rebuilt from the verified
history; they are not additional authorities. Unrelated manual activity is retained in the audit
trail with `classification=unrelated_manual` and excluded from managed projections.

An allocation epoch preserves the complete earlier history while changing the current universe,
sleeve cash, and reserve assignment. Because the ledger has no current market-value authority, an
epoch change is accepted only when every actual position is flat and no proposal is outstanding.
The assigned sleeve cash plus reserve must equal current replayed cash exactly. This deliberately
defers a requested reallocation rather than silently transferring capital committed to an open or
broker-active lifecycle. Allocation events cannot be corrected; a later allocation epoch is the only
way to change the assignment.

## Integrity and reconciliation

Ledger reads require canonical CSV bytes, valid hashes, monotonic timestamps, duplicate-event checks,
and replay accounting invariants. A private local head checkpoint also detects deletion of the final
event, which a hash chain alone cannot detect. `ledger export` writes the same checkpoint beside the
portable CSV as `.<csv-name>.head.json`; the CSV and checkpoint must be transferred together, and
`ledger import` verifies both before creating a local ledger. Checkpoint and reconciliation files live
beside the ledger under ignored paths.

Broker reconciliation consumes a synthetic-friendly CSV with this header:

```text
record_type,sleeve_id,instrument,quantity,cost_basis,cash
```

Use `record_type=position` for positions and `record_type=cash` for sleeve cash; an empty `sleeve_id`
denotes reserve cash. A successful reconciliation is tied to both the broker export checksum and the
ledger accounting projection. Submission/cancellation-only and `unrelated_manual` events do not
invalidate it; fills, fees, deposits, withdrawals, and managed adjustments do.

## CLI

```bash
uv run trading ledger init --managed-capital 100000 --universe \
  CIBR COPX DIA EEM EWJ EWT EWZ FCX FXI GLD INDA IWM NVDA SIVR SOXL SPY \
  TLT TQQQ TSLA TSM URA USO VGK VOO XBI XLU
uv run trading ledger verify
uv run trading ledger record --event-type deposit --amount 1000
uv run trading ledger allocate --allocation-epoch epoch-0002 \
  --sleeve-capital SPY=50000 QQQ=40000 --reserve-cash 10000
uv run trading ledger reconcile --broker-export broker-imports/account.csv
uv run trading ledger export backup/manual-execution-ledger.csv
uv run trading ledger import backup/manual-execution-ledger.csv --path state/manual-execution-ledger.csv
```

The initialization universe must exactly match the current tickers in
`trading.followup.STRATEGIES`. A different universe remains verifiable as a standalone ledger but
followup blocks new BUY proposals until the declared allocation epoch matches its selected universe.
Every allocation event changes the accounting hash, so broker reconciliation must be repeated before
any later Active strategy can produce a BUY.

`followup` verifies the ledger and current reconciliation before producing a new BUY. If ledger
verification fails, replayed positions are unavailable, so followup shows diagnostics but produces
neither BUY nor SELL proposals. If the ledger is valid but reconciliation is missing, failed, or
stale, confirmed-position exits remain available while new BUY proposals stay blocked.

Phase 7 submissions additionally retain strategy lifecycle, valid-result identity, completed-data
cutoff and bundle identity, ledger accounting hash, reconciliation status, and allocation epoch in
canonical event metadata. This evidence is immutable after the first submission. An exact retry
reuses it rather than rewriting it merely because current authorization evidence advanced; changed
proposal terms under the same proposal identity remain a conflict.
Replay also rejects correction events targeting submissions and histories containing overlapping
outstanding BUY proposals, including imported histories that bypass the current writer API.

An unfilled or partially filled entry proposal blocks a different BUY for that sleeve until the
proposal is filled or explicitly cancelled. Repeating the same input still returns the same
deterministic proposal ID, and changed terms for that identity are conflicts. An outstanding GTC stop
keeps its original proposal identity on later runs instead of creating another active stop. If its
price or quantity must change for a reason other than that proposal's own confirmed partial fills, the
reused identity produces a conflict until the old proposal is explicitly cancelled; the next run can
then create a replacement. A partially filled GTC stop remains the same immutable submission while
followup reports only its broker-active remaining quantity. Session-specific target and expiry
instructions continue to receive trading-date identities. Exit quantity, stop, target, and expiry are
derived from the replayed actual position and sleeve cash. For strategies with a trailing stop, the
effective stop also uses the verified position's average fill and the current hold window's high.

Expiry is fail-closed around broker order state: while a GTC stop remains submitted or partially
filled, followup repeats that stop and does not create an expiry SELL. If another exit or manual
adjustment closes the position first, the orphaned GTC stop blocks the sleeve's next BUY until an
explicit cancellation event confirms that the broker order is no longer active.
