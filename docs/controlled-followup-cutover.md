# Controlled followup cutover

Phase 7 moves followup authorization onto explicit lifecycle, result, data, ledger, and proposal
contracts while preserving management of confirmed positions. It remains dry-run manual trading;
no broker API, automatic submission, or live cutover is implemented.

## Cutover initialization

The first cutover event is allowed only after the manual ledger verifies, its current universe
exactly matches `trading.followup.STRATEGIES`, and its persisted broker reconciliation still matches
the ledger accounting hash and broker-export checksum. Initialization records every selected
strategy as `legacy_active` and enables global no-new-entry mode. It does not create, infer, or alter
broker positions.

```bash
uv run trading followup-state init
uv run trading followup-state status
uv run trading followup-state pause --reason "operator rollback"
uv run trading followup-state resume --reason "controlled activation window"
uv run trading followup-state retire --ticker SPY --experiment OLD_ID --reason "replacement selected"
uv run trading followup-state complete-retirement --ticker SPY --experiment OLD_ID --reason "verified flat"
```

`resume` removes only the global pause. It cannot authorize Legacy Active, Retiring, Shadow, Paused,
stale, invalid-result, wrong-epoch, unverified, or unreconciled BUY proposals. A missing, malformed,
rewritten, or truncated lifecycle registry is equivalent to no-new-entry mode.

The lifecycle registry is append-only, hash chained, atomically replaced under a bounded lock, and
protected by a private head checkpoint. Exact retries are idempotent; changed content under an
existing identity is a conflict. Runtime registry, lock, and checkpoint files are ignored by Git.

If an open position's entry proposal has no `authorization.strategy_id`, initialization fails until
the operator supplies an explicit mapping such as
`--position-owner SPY=spy_007_trend_pullback`. Existing proposal evidence takes precedence. The
mapping is persisted; current `STRATEGIES` is never silently treated as historical ownership.

## Strategy lifecycle and reporting

The operator report projects each selected ticker into the Phase 7 vocabulary:

- a Legacy Active, Retiring, or Paused strategy with a confirmed position reports `legacy position
  management`;
- unmigrated legacy definitions report `migration pending`;
- failed historical qualification reports `historical screen failed`;
- prospectively registered definitions report `Shadow` or `insufficient evidence`;
- a verified prospective promotion reports `Active`.

There may be at most one Active Strategy per ticker. Generic lifecycle transitions cannot create
Shadow or Active status. `followup-state shadow` verifies the exact passing Historical Screen,
Shadow registration, valid-result fingerprint, and recorded parity digest. Promotion uses
`activate_strategy` and a verifier boundary tied to an immutable
Shadow ID, qualification evaluation event, valid-result fingerprint, and passing migration-parity
digest. A replacement must first leave the old definition Retiring while its actual ledger position
is open; Retiring never authorizes a new BUY. The strategy that opened a confirmed position is read
from its entry proposal authorization, so changing `STRATEGIES` cannot silently transfer exit
ownership or parameters to the replacement. Generic transitions cannot move an Active or Retiring
definition around the retirement checks, and completion requires a freshly verified flat ledger.

## Order authorization

A BUY is actionable only when all of these facts are true at proposal time:

1. the strategy is Active and global no-new-entry mode is disabled;
2. the current persisted result is valid and has an exact result identity;
3. the exact validated data bundle equals the latest completed XNYS session and records both its
   cutoff and deterministic SHA-256 identity;
4. the ledger verifies and supplies its accounting identity;
5. broker reconciliation remains current;
6. the proposal uses the current allocation epoch; and
7. the sleeve has no actual position.

The submission event records the strategy identity and lifecycle, result identity, data cutoff and
bundle identity, ledger accounting hash, reconciliation state, and allocation epoch beside the
immutable proposal terms. Reusing a stable proposal ID with changed terms is a conflict. An exact
GTC retry keeps the immutable authorization evidence from its first submission even if the current
lifecycle, cutoff, or accounting evidence has advanced; the order sheet displays that original
evidence and does not rewrite history.

Immediately before a BUY append, the ledger lock protects a second validation of allocation epoch,
actual position, outstanding entry occupancy, proposal ownership, reconciliation, lifecycle pause,
Active proof, and current result. This prevents concurrent report runs or an operator rollback from
publishing stale risk. Submission terms and authorization cannot be changed by correction; cancel
and replace is required.

Lifecycle mutations and every ledger append share a per-directory manual-trading coordination lock.
The lifecycle check remains locked through ledger publication, so `pause`, retirement, fills, and
BUY submission cannot interleave across their separate files.

SELL proposals are a separate existing-position safety path. They require a verified actual ledger
position but do not require a strategy to remain Active or the global entry mode to be open. Their
quantity, average entry, stop, target, trailing stop, and expiry continue to derive from confirmed
fills rather than backtest state.

## Migration parity

`evaluate_data_access_parity` compares indicator cells, signal identities, and canonical trade
payloads produced from the same immutable snapshot. Every difference has a deterministic identity.
An unexplained difference blocks migration; an accepted data-consistency correction must name that
exact identity and include a non-empty reason. Duplicate or unused correction declarations fail
closed.

The currently selected detectors with auxiliary series declare those dependencies to the shared
CSV-backed market-data boundary. The detector cannot download them itself. Followup aligns each
auxiliary daily close to every primary decision session using the explicit same-session-after-close
policy (`publication_lag_sessions=0`, known publication timing, maximum observation lag three
sessions). A missing declaration, missing series, invalid frame, or uncovered decision session
blocks evaluation instead of disabling a filter. The primary and aligned auxiliary frames plus that
policy form the proposal's data-bundle identity.

A passing parity run must come from `run_verified_data_access_parity`. Its loader verifies and
returns one immutable bundle object, and both data-access paths execute against that same object.
The runner checks detector identity and
records checksums of both complete indicator/signal/trade outputs. Caller-assembled empty results are
not accepted by the registry. The verified run is appended for one exact strategy, snapshot, and
current definition fingerprint. `followup-state activate` then verifies that parity digest against
the hash-chained lifecycle history, the exact Shadow registration and activation-evaluation events
in `state/qualification-registry.json`, and the current valid persisted result fingerprint:

```bash
uv run trading followup-state activate \
  --ticker SPY \
  --experiment EXPERIMENT_ID \
  --shadow-id SHADOW_ID \
  --qualification-event-id ACTIVATION_EVENT_ID \
  --result-fingerprint SHA256 \
  --parity-digest SHA256 \
  --reason "prospective qualification passed"
```

Activation does not disable global no-new-entry mode. The operator must inspect status and use the
separate `resume` command only for an intended controlled window.

Retirement completion rechecks the lifecycle and ledger while appending. It requires the sleeve to
be flat and all BUY proposals to be filled or cancelled; the event records the verified ledger head.

The current selected fleet begins the controlled cutover as Legacy Active. Definitions remain
`migration pending` until their declared primary and auxiliary dependencies have been executed on
identical snapshots, parity evidence has passed, and Phase 6 historical and prospective evidence has
been recorded. Phase 7 code never treats existing legacy results or an unavailable migration run as
proof of completion.

## Allocation epochs and rollback

Universe or sleeve-capital changes use an append-only ledger allocation event. The transition is
limited to a flat ledger with no outstanding proposals and must preserve current cash exactly; this
is the conservative boundary when current position market values are unavailable. A successful
allocation event invalidates the prior broker reconciliation until reconciliation is repeated.

Rollback is `followup-state pause`. It appends a no-new-entry event without deleting lifecycle,
qualification, proposal, ledger, or reconciliation history. Verified existing-position management
continues.
