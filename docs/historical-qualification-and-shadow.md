# Historical qualification and prospective Shadow

Phase 6 replaces fixed Part A/B/C qualification with a recorded lifecycle. Legacy period results
remain inspectable, but they cannot grant Shadow or Active status. Historical evidence can produce
only `shadow-eligible`; even a complete prospective evaluation produces only
`activation-eligible`. Phase 6 always reports `authorized_for_live_orders=false`.

## Historical qualification plan

`build_historical_qualification_plan` freezes the definition fingerprint, development years,
annual folds, declared maximum holding and execution lags, dependency purge, opening embargo, base
and stress cost policies, stress limit, benchmark identities, random seed, bootstrap policy, and
every evaluation-session identity and pass threshold into a deterministic plan ID. The purge must cover the holding plus execution
dependency, and the embargo must cover the execution lag. Candidate trades that exceed those frozen
dependencies fail closed. A plan requires at least three complete consecutive development years and
five complete consecutive annual evaluation folds, and must be timestamped before its first
evaluation outcome. Each trade belongs to the one fold containing its signal date; its exit must be
complete inside that fold. Zero-signal folds remain explicit evidence.

The Historical Stability Screen runs each fold through the canonical isolated-sleeve engine under
base and stress costs. It requires at least 20 completed trades, three traded folds, 60% positive
traded folds, positive compounded return, profit factor above 1.1, positive stress return, stress
profit factor above 1, no stress drawdown breach, and no fold above 50% of trades or profits.

The three benchmark gates are cash, a preregistered family baseline, and deterministic
exposure-matched random entries. Random entries preserve each candidate's signal month, entry lag,
holding sessions, fold, and completed-trade count; inability to preserve that exposure fails closed.
The baseline input crosses an explicit verifier boundary bound to its frozen trial identity before
canonical evaluation.
Family-wise block bootstrap reads the complete verified trial-registry state and requires dated
daily excess-return evidence for every formal trial in the experiment family, including failed or
removed variants. Every trial must contain exactly the same unique, chronological session identities
frozen by the qualification plan.
Duplicate trials, missing or shifted sessions, non-finite returns, or an incomplete legacy selection
history block qualification.

## Prospective Shadow

A passing historical screen may be formally registered as Shadow only after its plan and screen
events have been persisted. Registration binds the selected trial, immutable definition snapshot
digest and byte count, definition fingerprint, prospective start, activation checkpoint, cost
policies, and activation policy. The persistence boundary verifies the definition blob and records
its own UTC time; a new registration's prospective start must match that time. Observations on or
before the registration date—including legacy Part C—are excluded.

Shadow candidates create deterministic, non-actionable paper proposal IDs from only the frozen
Shadow identity and proposal-time signal, entry, and action terms; later exit outcomes do not change
the ID. Completed paper trades become canonical simulated fills linked to those proposals; they
never become broker fills or actual positions. Evidence declares a completed market-data cutoff and
an aware observation clock; the cutoff and complete row sequence are verified against the XNYS
session calendar. Evidence cannot use candidates with future exits. Checkpoints are monotonic:
sessions and cutoffs cannot decrease, prior periods cannot be backfilled, and
previous proposal/fill history must remain an exact prefix.

Activation evaluation requires its frozen checkpoint, at least 252 completed sessions, 12 completed
simulated fills, positive base and stress returns, base and stress profit factors above one, stress
drawdown compliance, and an explicit fail-closed critical-drift assessment. Phase 6 records that
assessment but does not define the predictive drift envelopes reserved for Phase 8. Low-frequency
strategies remain `shadow-insufficient-evidence`; thresholds are not relaxed. An outcome-relevant
definition change creates a new trial and Shadow registration linked by `prior_shadow_id`, with no
evidence carryover.

## Persistence and result evidence

`QualificationRegistry` stores an append-only, hash-chained, atomically replaced event sequence
under a bounded file lock:

1. `historical_plan`
2. `historical_screen`
3. `shadow_registration`
4. one or more `shadow_evidence` checkpoints
5. matching `activation_evaluation` checkpoints

Exact retries are idempotent; changed content under the same event identity is a conflict. A private
head checkpoint supplements the hash chain so final-event deletion is also detected. Missing,
rewritten, truncated, or partially stripped history fails verification. A screen requires its persisted
plan and completed fold outcomes. Shadow registration requires the persisted passing screen and
matching family, definition, selected trial, and cost policies. Every registry read re-verifies each
immutable definition snapshot. Prospective evidence requires the registered frozen definition, and
activation requires evidence for the same `as_of` date; the persistence boundary recomputes gate
truth from that evidence and resolves the trial's current definition through an injected trusted
boundary rather than trusting a caller's eligible flag or fingerprint. Result projection omits a
stale activation when a newer evidence checkpoint has not yet been evaluated.

`result_sections()` projects verified registry events into schema-v3 `development_summary`,
`historical_stability_folds`, and `shadow_evidence`. Result validity independently checks complete
fold/session policies, recomputes historical aggregates and gate truth, validates random benchmark
exposure plus proposal/fill schemas, and recomputes activation gates. It fails closed on incomplete
or contradictory evidence, changed Shadow identity or definition, historical evidence claiming
Active, or any Shadow evidence claiming live-order authorization.

The default local registry is `state/qualification-registry.json`. It and custom
`qualification-registry*.json` files are ignored by Git. Inspect it without network access or writes:

```bash
uv run trading qualification status
uv run trading qualification status --path state/qualification-registry.json
```

Phase 6 does not submit orders, update followup strategy state, authorize activation, or perform the
Phase 7 controlled cutover.

Phase 7 consumes this evidence only through a separate verified activation boundary. A generic
followup lifecycle transition cannot create Active status; promotion must identify the exact Shadow
registration and activation-evaluation event, current valid-result fingerprint, and passing
data-access parity evidence. See
[controlled-followup-cutover.md](controlled-followup-cutover.md).
