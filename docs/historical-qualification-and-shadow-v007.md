# Historical qualification, frozen selection boundaries, and prospective Shadow (v007)

Phase 6 records Historical, retrospective-confirmatory, and Shadow lifecycle evidence. Historical
evidence can produce only `shadow-eligible`; retrospective evidence can produce only
`retrospectively-supported`; prospective Shadow can produce only `activation-eligible`. None of
these states alone authorizes live orders.

## Evidence classification and retrospective boundary

Before outcome inspection, every proposed evaluation period is classified for the exact asset and
lineage as `verified-clean`, `known-contaminated`, or `provenance-unknown`. Only `verified-clean`
with complete relevant trial history may enter clean Historical Evaluation. Completed data with
unknown or contaminated provenance may enter only an explicitly frozen
`retrospective-confirmatory` plan.

Retrospective registration creates a current-time `retrospective_selection_checkpoint`. It freezes
the selected trial, distinct baseline, and complete registered family without claiming a
future-only Forward Selection Epoch. Passing is non-promotional and cannot register Shadow,
replace clean Historical evidence, or authorize activation.

## Qualification role calendars

Every plan freezes exact evaluation sessions and annual folds. The default clean Historical path
also freezes the three complete consecutive Development years immediately before the first five
or more consecutive annual Evaluation folds.

A retrospective study may instead use a nonstandard chronology, including completed Development
context later than its retrospective evaluation. Such a plan must use the explicit role-calendar
registration inputs and serialize three exact completed-session inventories:

- `development_sessions`: at least three complete consecutive Development-context years;
- `warmup_sessions`: non-outcome observations strictly before the first evaluation session and
  sufficient for the declared dependency window; and
- `evaluation_sessions`: the complete consecutive retrospective annual folds.

All inventories must be unique, chronological, non-empty, and pairwise disjoint. Development
context is governance and selection evidence only; it is never added to screen return series.
Warmup sessions may supply indicators and declared dependencies but never signals, fills,
cooldown, positions, P&L, capital, benchmarks, or performance. Evaluation returns and family-wise
selection-adjustment inputs must still match `evaluation_sessions` exactly.

Partial overrides fail closed. Explicit role calendars are prohibited for clean Historical plans.
Unassigned sessions remain quarantined or out of scope. An existing plan without an explicit role
calendar remains valid only under the original immediately-preceding Development chronology.

## Plan registration

The production CLI takes the current UTC clock and has no backdating option. It captures the exact
research definition and released workflow policy set, verifies the selected and baseline trials,
freezes the family universe, generates XNYS session identities, and atomically appends the plan.

Default clean Historical registration remains:

```bash
uv run trading qualification plan register \
  --research <family/trial> \
  --workflow workflows/<released-workflow>--vNNN \
  --family-baseline-trial-id <trial-id> \
  --evaluation-years 2027 2028 2029 2030 2031 \
  --maximum-holding-sessions 5 \
  --execution-lag-sessions 1 \
  --dependency-sessions 6 \
  --embargo-sessions 1 \
  --random-seed 17 \
  --evidence-role historical \
  --evidence-classification verified-clean \
  --audit-justification "append-only clean-holdout evidence" \
  --trial-history-complete
```

An explicit retrospective calendar additionally requires all of:

```bash
  --development-years 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 \
  --warmup-start 2009-01-01 \
  --warmup-end 2009-12-31 \
  --evidence-role retrospective-confirmatory
```

Supplying only some calendar inputs, overlapping roles, sparse or incomplete Development years,
insufficient warmup, warmup on or after Evaluation, or retrospective inputs under a workflow that
does not authorize the checkpoint fails before registry mutation.

## Folds, dependencies, and screen

Plans require at least five complete consecutive annual evaluation folds. Dependency purge must
cover maximum holding plus execution lag, and opening embargo must cover execution lag. Every
trade belongs to the fold containing its signal date and must exit within that fold. Zero-signal
folds remain explicit evidence.

The screen recomputes canonical isolated-sleeve outcomes under base and stress costs. It requires
the frozen trade, fold, return, profit-factor, drawdown, concentration, cash, distinct-baseline,
exposure-matched random-entry, and complete-family selection-adjustment gates. Exact manifests for
every frozen family trial must cover the final evaluation session and have valid formal
observations. The screen accepts no caller-supplied pass flag.

Family-wise selection adjustment consumes the plan's one frozen selection boundary:

- clean Historical uses `forward_selection_epoch` and its `started_at`;
- retrospective-confirmatory uses `retrospective_selection_checkpoint` and its `frozen_at`.

When the registry discloses incomplete prior selection history, the boundary must make the same
disclosure and must exactly match the registered family universe and selected trial. Every included
trial requires a parseable first-registration timestamp no later than the applicable boundary
time. A missing boundary, dual boundaries, disclosure mismatch, family or selected-trial mismatch,
missing timestamp, or late trial fails closed before selection-adjusted confidence is computed.
The retrospective checkpoint remains non-forward and non-promotional.

Release-readiness validation must be provider-free and exercise the production path from plan
registration through persisted-plan reload, screen coordination, and the actual family-wise
selection-adjustment evaluator. It must cover the successful forward and retrospective paths plus
negative cases for every fail-closed guard above. Registration-only, serialization-only, direct
domain-only, or coordinator-only tests do not satisfy this requirement.

## Compatibility and persistence

Existing Historical and retrospective plans retain their original payloads and deterministic plan
IDs. The optional `role_calendar` object is emitted only for new explicit retrospective plans.
Registry deserialization remains backward compatible, while persistence and result validation
reject nonstandard Development chronology without the explicit object or any inconsistent role
inventory.

No plan may rewrite a prior event, import retrospective status into Shadow, or change session roles
after outcome inspection. Outcome-informed changes require a new trial or study and make the viewed
period Development context for that changed lineage.

## Prospective Shadow

Only a persisted passing clean Historical screen may register prospective Shadow. Registration
binds exact plan, trial, definition snapshot, policy, cost, prospective-start, and activation
checkpoint identities. Pre-registration observations do not count. Definition or outcome-relevant
execution changes terminate the Shadow lineage and require full requalification.

Shadow remains non-actionable paper evidence. Missing, stale, corrupt, rewritten, contradictory,
or non-replayable evidence fails closed. Activation evaluation never bypasses controlled cutover,
ledger, reconciliation, allocation, parity, drift, or manual-operator guards.
