# Historical qualification, retrospective confirmation, and prospective Shadow (v005)

Phase 6 replaces fixed Part A/B/C qualification with a recorded lifecycle. Legacy period results
remain inspectable, but they cannot grant Shadow or Active status. Historical evidence can produce
only `shadow-eligible`; even a complete prospective evaluation produces only
`activation-eligible`. Phase 6 always reports `authorized_for_live_orders=false`.

## Clean-evidence classification and retrospective confirmation

Before an evaluation plan inspects outcomes, every proposed evaluation period is classified for
the exact asset and research lineage as `verified-clean`, `known-contaminated`, or
`provenance-unknown`. `verified-clean` requires append-only evidence that the outcomes did not
influence the strategy family, definition, parameters, thresholds, selection, or interpretation,
plus complete relevant trial history. Known legacy use is `known-contaminated`; missing proof,
including incomplete legacy selection history, is `provenance-unknown`. A different researcher,
new study identity, or promise not to read legacy documents does not restore clean status.

Only `verified-clean` sessions may enter a clean Historical plan. Every asset may instead opt into
an exact `retrospective-confirmatory` plan over completed data. The plan freezes the same annual
fold, dependency, cost, benchmark, family-selection, and challenge identities as Historical, but
serializes its evidence role, clean-evidence audit, and a
`retrospective_selection_checkpoint`. The checkpoint is distinct from a future-only
`ForwardSelectionEpoch`; it freezes the selected trial and complete family universe at the current
UTC time without claiming that already-completed outcomes are future data. A passing retrospective screen records only
`retrospectively-supported`; a failing complete screen records `retrospective-screen-failed`.
Neither disposition can register Shadow, offset a clean Historical gate, authorize activation, or
authorize live orders. Outcome-informed changes create a new trial or study and make the viewed
period Development context for that changed lineage.

## Historical qualification plan

`build_historical_qualification_plan` freezes the definition fingerprint, evidence role and audit
when present, development years,
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
history block retrospective qualification.

When the global registry discloses incomplete legacy selection history, it is never cleared or
relabelled complete. A new program may instead register a `ForwardSelectionEpoch` before its first
evaluation outcome. The epoch freezes the selected trial, a distinct family baseline, and every
currently registered non-legacy trial in that exact experiment family. All evaluation sessions are
future sessions relative to registration. A trial added to the family after registration invalidates
the epoch, and a screen must restart from a new plan; past outcomes and older Phase 9 evidence cannot
be imported into the epoch.

The production CLI deliberately has no `--created-at` option. It takes the current UTC clock,
generates complete XNYS development and evaluation sessions, captures the selected identity's
current exact definition, verifies the frozen family universe against the append-only trial
registry, and atomically appends the plan. Workflow-native identities use `--research` with an
exact released `--workflow`; `--experiment` remains only for compatible frozen legacy identities:

```bash
uv run trading qualification plan register \
  --research <family/trial> \
  --workflow workflows/<released-workflow>--vNNN \
  --family-baseline-trial-id <registered_baseline_trial_id> \
  --evaluation-years 2027 2028 2029 2030 2031 \
  --maximum-holding-sessions 5 \
  --execution-lag-sessions 1 \
  --dependency-sessions 6 \
  --embargo-sessions 1 \
  --random-seed 17 \
  --evidence-role historical \
  --evidence-classification verified-clean \
  --audit-justification "append-only clean-holdout evidence identity" \
  --trial-history-complete
```

A retrospective registration uses `--evidence-role retrospective-confirmatory` with the honest
classification and justification. It is accepted only when the exact released workflow contract
contains that checkpoint; a draft workflow or v004 cannot authorize it.

The family baseline must already be a distinct formal trial in the selected experiment family.
Registration fails without it and does not manufacture a comparator. The default base/stress costs,
Phase 6 thresholds, 1,000 random samples, 1,000 bootstrap repetitions, and 20-session bootstrap
blocks are serialized into the immutable plan; explicit pre-registration changes are also frozen,
and the domain validators reject non-positive policies or weaker qualification gates. A family may
have only one open Forward Selection Epoch, preventing parallel plan variants from being selected
after their outcomes are known.

After the final frozen fold completes, the screen CLI requires one exact formal manifest for every
frozen family trial. Each manifest must match the trial's current exact definition, cover the final
evaluation session, and have a successful `online` or `offline` registry observation that was valid
for that exact snapshot. The CLI reruns all strategies from immutable bundles, derives daily sleeve
returns, repeats the family selection adjustment, recomputes every Historical Screen gate, and only
then appends the result:

```bash
uv run trading qualification screen run \
  --plan-id <historical-plan-id> \
  --workflow workflows/<released-workflow>--vNNN \
  --trial family/selected=results/selected/<snapshot>.snapshot.json \
  --trial family/baseline=results/baseline/<snapshot>.snapshot.json
```

Supplying a `passed` flag or precomputed screen payload is not supported.
Workflow-native replay resolves definitions through `src/trading/research_definitions/`, the exact
released workflow policy set, immutable definition snapshots, and formal trial observations. It
does not route through the closed `src/trading/experiments/` inventory.

## Prospective Shadow

A passing clean historical screen may be formally registered as Shadow only after its plan and screen
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
It also verifies evidence-role/audit consistency, the distinct retrospective dispositions, and
rejects any Shadow lineage sourced from a retrospective plan.

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
