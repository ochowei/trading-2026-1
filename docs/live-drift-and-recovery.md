# Phase 8 — Live drift and recovery

Phase 8 is a dry-run evidence and authorization layer. It does not call a broker, submit an
order, or perform a live cutover. The existing Phase 7 lifecycle remains the authority for
qualification, strategy ownership, Active/Retiring status, and the global no-new-entry mode.
Phase 8 adds a separate per-strategy drift-health overlay.

## Domain contract

Before a strategy can be Active, operators freeze one `PredictiveDriftEnvelope` from the accepted
historical folds and Shadow evidence. The envelope contains:

- the strategy and research-definition fingerprint;
- source identities for the historical and prospective evidence;
- Decimal-only expectations for performance, signal, execution, and portfolio utilization/concentration;
- minimum samples and observation windows;
- the fixed completed-XNYS-session checkpoint interval and bootstrap policy; and
- the data, ledger, reconciliation, execution, and stress-risk hard-guard families.

The envelope identity is a canonical SHA-256 digest. At activation its source identities must be
the exact passing Historical Screen event and the exact Shadow evidence event used by the eligible
activation evaluation, and all five required metric families must be present. The bootstrap fields
record the frozen derivation policy that produced the boundaries; runtime classification applies
those already-derived Decimal boundaries and each metric's own session window. The envelope is
persisted after its source evidence exists but before activation, and cannot be replaced once
activation is bound. A changed strategy-definition fingerprint is a new trial and must complete
Historical Screen, Shadow, and prospective qualification again.

Each completed session appends one immutable `DriftObservation`. Metric values are serialized as
canonical Decimal strings. Performance and signal observations bind an exact verified Phase 6
Shadow evidence event; their cumulative completed-paper-trade count is derived from its simulated
fills. Execution and portfolio observations bind the verified manual-ledger accounting hash.
Confirmed fills and verified ledger positions are evidence; an assumed broker fill is not.
Observations must match the frozen envelope, use increasing sessions already completed at their
observation timestamp, and retain canonical timestamps. Unexpected metric or hard-guard families
fail closed.

## Health and transitions

The overlay has three operational states:

| State | Meaning | New BUY | Existing position |
| --- | --- | --- | --- |
| Healthy | All scheduled metrics are normal and no hard guard is active. | Allowed only after every Phase 7 guard also passes. | Managed normally. |
| Watch | A metric is in the adverse 20% boundary, or evidence is temporarily inconclusive. | Allowed under heightened monitoring unless another guard blocks it. | Managed normally. |
| Paused | A metric reaches the adverse 5% boundary, a hard guard is active, or two consecutive scheduled checkpoints are Watch. | Always blocked. | Continue verified target/stop/expiry management and paper execution. |

Boundary comparisons are inclusive. An ordinary single loss inside the frozen envelope does not
pause a strategy. Missing or insufficient checkpoint evidence is fail-closed Watch evidence, so two
consecutive inconclusive scheduled checkpoints also satisfy persistent Watch. A hard guard blocks
new BUY authorization immediately; it does not wait for the next checkpoint. A scheduled checkpoint
is a deterministic ordinal and XNYS session derived from the frozen activation anchor. Checkpoint
state is recomputed from the event history rather than accepted from an operator-supplied state
field.

## Recovery

Recovery is an append-only, evidence-derived transition. Editing a state field, deleting an event,
or changing a threshold never recovers a strategy.

Normal recovery requires all of the following after the pause:

1. 126 later completed sessions;
2. six completed Shadow/paper trades;
3. every hard guard cleared; and
4. two consecutive scheduled checkpoints classified as normal.

When the pause cause is exclusively data, ledger, or reconciliation integrity, the expedited
data/ledger-only gate requires reconciliation plus two distinct clean checks after the pause and
no active hard guard. It does not waive a performance, signal, execution, utilization,
concentration, or stress-risk pause.

## Persistence and concurrency

`LiveDriftRegistry` is a private per-strategy append-only event log. The default followup directory
is `state/live-drift/`; files are ignored by Git and must not contain broker exports, credentials,
or personal trading data in a commit. Every event has a canonical payload, sequence, previous hash,
and event hash. A sidecar head checkpoint stores the event count, checksum, and head hash.

Writes use the same bounded coordination lock and atomic replacement policy as the manual ledger.
Readers replay and verify the complete chain. Semantic replay also verifies envelope identity,
monotonic session/timestamp ordering, checkpoint schedule and classification, hard-guard state,
and recovery gate statistics. Duplicate identical event requests are idempotent; conflicting or
out-of-order requests fail closed.

The Phase 7 followup authorizer receives the overlay as additional evidence. For BUY, lifecycle
must still be Active, no-new-entry must be disabled, the result/data/ledger/reconciliation/epoch
guards must pass, the overlay must not be Paused, and no drift hard guard may be active. A Paused
overlay does not disable SELL of a verified actual position.

## Read-only and state-changing commands

These commands operate only on local private evidence and never contact a broker:

```text
uv run trading drift status --path state/live-drift/<strategy>.json
uv run trading drift freeze --path state/live-drift/<strategy>.json --envelope envelope.json
uv run trading drift activate --path state/live-drift/<strategy>.json \
  --strategy-id SPY/spy_007_trend_pullback --envelope-id <digest> \
  --activation-event-id <phase-7-event-id>
uv run trading drift observe --path state/live-drift/<strategy>.json \
  --session YYYY-MM-DD --metric performance_return=0:6 \
  --shadow-evidence-event-id shadow-evidence:<shadow-id>:YYYY-MM-DD
uv run trading drift checkpoint --path state/live-drift/<strategy>.json \
  --ordinal 1 --session YYYY-MM-DD
uv run trading drift clean-check --path state/live-drift/<strategy>.json \
  --session YYYY-MM-DD --evidence-identity <digest>
uv run trading drift recover --path state/live-drift/<strategy>.json \
  --current-session YYYY-MM-DD \
  --ledger-path state/manual-execution-ledger.csv \
  --reconciliation-path state/manual-reconciliation.json
```

`clean-check` and `recover` verify the current manual ledger and persisted broker reconciliation;
the accounting hash is the clean-check evidence identity. Recovery cause, clean-check sessions, and
hard-guard clearance are derived from replay and cannot be supplied as operator assertions.
Performance and signal observations resolve their cumulative paper-trade count from the exact
verified Phase 6 Shadow evidence event. Execution and portfolio observations automatically bind
the current verified manual-ledger accounting hash; callers cannot supply a trade count directly.

`followup-state activate` additionally requires `--drift-envelope-id` and binds the verified Phase
7 activation event to the frozen envelope. `trading followup` reads the overlay from the private
directory and remains a dry-run manual proposal report.
