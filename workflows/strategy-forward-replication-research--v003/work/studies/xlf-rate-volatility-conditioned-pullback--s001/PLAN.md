# Plan: XLF Rate-Volatility-Conditioned Pullback Research

## Inputs and frozen identities

### Governance and authority

- Workflow: `strategy-forward-replication-research@v003` at
  `workflows/strategy-forward-replication-research--v003`.
- Workflow release SHA-256:
  `9c5a554751a70d6c286fa0ca938ee171cc5da81d2e683d29b11ba06579aad183`.
- Workflow definition SHA-256:
  `11cebc16588c2feae2637128b4b18a015d0de65507ee47096ae0a3e8aec0370f`.
- Composite policy set:
  `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.
- Human research owner and preregistration/candidate-freeze approver:
  `ochowei@gmail.com`.
- Researcher/operator for planning and Development evidence:
  `codex-primary-researcher-xlf-s001`.
- This is a new workflow-native family. `revisits=null`; no legacy experiment identity is changed.

### Market data and availability

- Primary: Yahoo auto-adjusted daily OHLCV for `XLF`, XNYS-complete coverage, required from
  1998-12-16.
- Auxiliary for gated candidates: Yahoo auto-adjusted daily OHLCV for `^MOVE`, provider-
  observation coverage, required from 1998-12-16.
- `^MOVE` publication time is treated as unknown. Each signal decision uses only the most recent
  observation available after a one-XNYS-session publication lag, with maximum permitted
  observation lag of three XNYS sessions. The aligned observation date, available session, and
  lag must be preserved by the market-data bundle.
- A full refresh and immutable snapshot for every declared series is required after
  preregistration and before any formal run. Existing mutable cache content is not evidence.
- Every formal observation must bind the exact data manifest, Research Definition Snapshot,
  policy set, v003 release/workflow hashes, complete Git HEAD, canonical argv, and exact
  orchestration source bytes required by v003.

### Data roles and non-overlap

| Role | Frozen sessions |
| --- | --- |
| Warmup only | 1998-12-16 through 1999-12-31 |
| Development | 2000-01-03 through 2020-12-31 |
| Historical annual folds | calendar years 2021, 2022, 2023, 2024, and 2025 |
| Quarantined | 2026 sessions before any future Shadow registration; never backfilled into Shadow |
| Shadow | prospective sessions only after a persisted passing Historical screen and current-time registration |

For Development and each Historical fold, the first 21 completed primary sessions are warmup-only
and cannot generate entries. The final 11 primary sessions are purged from signal generation so a
one-session-lag entry and ten-session holding period cannot cross the role or annual-fold boundary.
No position carries into a role or fold. Each trade belongs to its signal-date fold and must enter
and exit within that same fold.

### Candidate inventory and trial accounting

`maximum_trials=6`. Every viewed outcome-relevant semantic definition, including a failed,
abandoned, baseline, or robustness-only definition, consumes one slot. Repeating an exact frozen
fingerprint adds an observation but not another trial.

| Stable identity | Role | Frozen difference |
| --- | --- | --- |
| `xlf-rate-volatility-conditioned-pullback/move-direction-cap-3` | selection candidate | aligned `^MOVE` three-session point change <= +3 |
| `xlf-rate-volatility-conditioned-pullback/move-direction-cap-5` | selection candidate | aligned `^MOVE` three-session point change <= +5 |
| `xlf-rate-volatility-conditioned-pullback/move-direction-cap-7` | selection candidate | aligned `^MOVE` three-session point change <= +7 |
| `xlf-rate-volatility-conditioned-pullback/ungated-pullback-baseline` | distinct simple baseline | same XLF pullback and execution, no auxiliary gate |
| `xlf-rate-volatility-conditioned-pullback/selected-cap-minus-one-robustness` | robustness only | selected cap minus one MOVE point; cannot win selection |
| `xlf-rate-volatility-conditioned-pullback/selected-entry-lag-two-robustness` | robustness only | selected cap with entry delayed to the second next open; cannot win selection |

The two robustness definitions are materialized only after Development selects a candidate, using
the deterministic construction above. No seventh semantic trial is permitted.

### Frozen strategy and execution semantics

- Signal on completed session `t`: XLF adjusted close is at or below
  `rolling_mean_20 - 2.0 * rolling_sample_std_20`, and XLF ten-session adjusted-close return is
  at or below -4%.
- Gated candidates additionally require the backward-as-of aligned `^MOVE` close change over three
  decision sessions to be at or below the candidate cap.
- Entry: market at the next XNYS open (`t+1`); the delayed-entry robustness uses `t+2`.
- Exit: market at the XNYS open ten completed sessions after entry. There is no target, stop,
  trailing stop, limit order, or intrabar trigger.
- Unfilled handling: next-open market events are considered filled when a verified bar exists;
  a missing/non-finite open is an integrity failure, not an inferred fill. Purged or incomplete
  final signals do not become candidates.
- Canonical isolated sleeve: normalized capital 1.0, fractional quantity, one open position,
  no leverage, pyramiding, rebalancing, or capital transfer. Overlapping candidates are retained
  as raw evidence and canonically skipped with `position_already_open`.
- Gross candidates contain no embedded costs. Base and stress entry/exit slippage and fees come
  only from the exact released `canonical-execution@v001` policy selected by v003.

## Method and stages

### 1. Preregistration

Validate all four released policy pins, source identities, data declarations, trial inventory,
calendar boundaries, gates, and exact human approval. Generate `PREREGISTRATION.json` before any
XLF or MOVE refresh, snapshot, formal execution, metric calculation, result inspection, or trial
ranking. After preregistration, `HYPOTHESIS.md` and `PLAN.md` are immutable.

### 2. Development and candidate selection

After explicit stage advancement, perform one full refresh of XLF and MOVE, create immutable
manifests and definition snapshots, and run all three candidates plus the baseline offline using
only Development-eligible trades. Do not calculate, display, serialize into the Development gate,
or use 2021-2025 outcome metrics during selection.

A candidate is Development-eligible only if it has at least 30 completed base-net trades across at
least ten traded calendar years, base compounded return > 0, base profit factor > 1.1, stress
compounded return > 0, stress profit factor > 1.0, stress maximum drawdown <= 15%, no unresolved
parity/integrity difference, and base-net daily-equity Sharpe at least 0.25 above the ungated
baseline. Rank every eligible candidate by base-net daily-equity Sharpe descending; ties use the
stable identity order cap-3, cap-5, cap-7. If any required candidate or baseline is invalid, stop
without partial ranking. If none is eligible, the round fails.

Persist the complete Development candidate set, observation identities/checksums, eligibility
table, ranking, and rationale. Materialize the two deterministic robustness definitions for the
selected cap. Human owner approval is required before candidate freeze or Historical access.

### 3. Historical Evaluation and robustness

After candidate freeze approval, evaluate only the frozen selected candidate, distinct baseline,
and two robustness-only definitions on five annual folds for 2021-2025. Recompute the candidate
under gross, base, and stress costs using the canonical sleeve. Record zero-signal folds and the
chained five-fold capital path.

Required challenges are cash; the ungated baseline; 1,000 exposure-matched random-entry replicas
using seed `20260812`; a family-wise 20-session block bootstrap over all three selection candidates
with 1,000 replicas and the same seed; the cap-minus-one and delayed-entry definitions; stress
costs/worse fills; deterministic omission of 10% of otherwise executable entries using the same
seed; and per-fold market-regime results. Challenges may falsify the selected candidate but cannot
replace it.

Viewing any 2021-2025 outcome consumes those folds for this round. Any Historical failure ends the
round; modified candidates cannot reuse those folds as validation.

### 4. Prospective Shadow and later stages

Only a persisted passing Historical screen may be registered for prospective Shadow at current
UTC. Pre-registration and pre-Shadow 2026 sessions cannot be backfilled. Shadow uses non-actionable
paper proposals and canonical simulated fills only, for at least 252 completed sessions and 12
completed fills. Later activation and monitoring stages remain subject to every v003 authority,
ledger, reconciliation, allocation, drift, and no-new-entry guard; this study never authorizes
broker access or orders.

## Metrics and outcome rules

### Historical gates

All gates are conjunctive:

- at least five complete, consecutive, non-overlapping annual folds;
- at least 20 completed Historical trades, at least three traded folds, and at least 60% positive
  traded folds;
- chained base compounded return > 0 and base profit factor > 1.1;
- chained stress compounded return > 0 and stress profit factor > 1.0;
- stress maximum drawdown <= 15%;
- no fold contributes more than 50% of total completed trades or more than 50% of total positive
  profit;
- selected candidate base-net daily-equity Sharpe exceeds the ungated baseline by at least 0.25;
- selected candidate compounded return exceeds cash, the ungated baseline, and the 90th percentile
  of exposure-matched random-entry returns;
- family-wise block-bootstrap selection confidence is at least 90%;
- cap-minus-one, delayed-entry, stress/worse-fill, 10%-missed-entry, and annual-regime challenges
  contain no negative stress return, profit factor <= 1.0, stress drawdown > 15%, unresolved
  integrity difference, or evidence that the claimed MOVE direction is reversed.

### Outcomes

- `pass`: every Historical identity and gate above is complete and passing. This grants only
  `shadow-eligible` and requires a separate prospective registration.
- `fail`: a complete reproducible Development or Historical gate fails, or the six-trial budget is
  exhausted without an eligible candidate.
- `insufficient-evidence`: permitted only in an open prospective Shadow stage after its minimum
  duration has elapsed but completed fills remain below 12, or another v003 checkpoint explicitly
  permits continued accumulation.
- `indeterminate`: required identity, data, source, policy, provenance, replay, or gate evidence is
  missing, stale, corrupt, conflicting, or unverifiable. Advancement stops; only the same frozen
  evidence may be repaired.

Shadow must independently satisfy v003 minimum duration/fills, positive base and stress returns,
base and stress profit factors > 1.0, stress drawdown <= 15%, and critical-drift requirements. A
Shadow pass grants only `activation-eligible`, not live authority.

## Deviations and stopping rules

After preregistration, do not change the hypothesis, data roles, candidate inventory, trial budget,
indicator formulas, thresholds, auxiliary availability, selection rule, baseline, costs, execution,
purge/embargo, gates, seeds, or outcome rules. Any such change requires cancellation and a new
study with an exact `revisits` path; it cannot reuse viewed Historical evidence.

Pause advancement on incomplete/stale market data, digest drift, missing source bytes, invalid
manifest, parity/provenance mismatch, partial candidate availability, or any v003 fail-closed
condition. Record deviations append-only in `EVIDENCE.md`; never repair an unfavorable outcome,
hide a trial, expand the budget, loosen a cap/gate, or substitute a mutable `latest` pointer.

Terminate this round when no Development candidate is eligible, the trial budget is exhausted, a
Historical or Shadow gate fails, a frozen definition changes materially, required evidence cannot
be recovered, or the human owner stops the study. `EVIDENCE.md` remains execution-only and
`CONCLUSION.md` remains untouched until independent review.
