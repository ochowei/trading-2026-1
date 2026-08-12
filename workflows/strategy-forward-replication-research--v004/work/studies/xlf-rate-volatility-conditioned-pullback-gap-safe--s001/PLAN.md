# Plan: XLF Gap-Safe Rate-Volatility-Conditioned Pullback Research

## Inputs and frozen identities

### Governance, lineage, and authority

- Study: `strategy-forward-replication-research@v004/S001` at
  `workflows/strategy-forward-replication-research--v004/work/studies/xlf-rate-volatility-conditioned-pullback-gap-safe--s001`.
- Workflow: `strategy-forward-replication-research@v004` at
  `workflows/strategy-forward-replication-research--v004`.
- Workflow `RELEASE.json` SHA-256:
  `5e00e3ed5b4d87de39f4db48ac5a523cdb82992b737a5306e8928a4073320430`.
- Workflow definition SHA-256:
  `d176471dd099bf55274748d82957cd5a410b40ddda5e38c9e8d69926a66431da`.
- Canonical source Git HEAD at preregistration preparation:
  `005500bea15f2a646c8b5b8a17afe5c46158c787`.
- Composite policy set:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Human research owner and preregistration/candidate-freeze approver:
  `ochowei@gmail.com`.
- Researcher identity: `codex-primary-researcher-xlf-v004-s001`.
- Exact predecessor:
  `workflows/strategy-forward-replication-research--v003/work/studies/xlf-rate-volatility-conditioned-pullback-publication-lag-safe--s003`.
- S001, S002, and S003 under v003 remain immutable provenance. This local v004 identity is `S001`;
  there is no cross-version `S004` identity.

### Released policy pins

| Family | Version | `RELEASE.json` SHA-256 |
| --- | --- | --- |
| `us-equity-market` | `v002` | `9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` |

No implicit `latest` policy is permitted. Every formal Research Definition Snapshot and result
must bind this exact composite set and the v004 workflow release.

### Market data, availability, and data roles

- Primary: Yahoo auto-adjusted daily OHLCV for `XLF`, complete XNYS-session coverage, required from
  2002-11-13.
- Auxiliary for gated candidates: Yahoo auto-adjusted daily OHLCV for `^MOVE`, provider-
  observation coverage, required from 2002-11-13.
- MOVE publication time is unknown. Every decision uses only the latest observation available
  after one completed XNYS publication-lag session. Maximum observation lag is exactly three XNYS
  sessions; it may not be increased.
- Auxiliary excess-lag mode is exactly `mark_unavailable` under `us-equity-market@v002`. The
  backward-as-of row, `ObservationDate`, `AvailableSession`, and `ObservationLagSessions` remain
  audit evidence, while `ObservationAvailable=false` suppresses the raw signal, candidate, and
  trade. Silent dropping, forward-filling eligibility, treating stale values as current, or
  outcome-time reclassification is prohibited.
- The preregistered unavailable-decision inventory inherited from the outcome-free S003
  availability audit is exactly 2013-03-21, 2013-03-22, and 2013-03-25. Each used the 2013-03-15
  MOVE observation first available on 2013-03-18, at actual lags four, five, and six sessions.
  Formal execution must reproduce this inventory exactly or stop `indeterminate`; no candidate
  outcome may be inspected before that verification.

| Role | Frozen completed sessions |
| --- | --- |
| Warmup only | 2002-11-13 through 2003-12-31 |
| Development | 2004-01-02 through 2020-12-31 |
| Historical Evaluation | Five annual folds: 2021, 2022, 2023, 2024, and 2025 |
| Quarantined | All 2026 sessions before any future current-time Shadow registration |
| Shadow | Prospective sessions only after a persisted passing Historical screen and registration |

For each Development/Historical segment, the first 21 completed primary sessions are warmup-only
and the final 11 primary sessions are purged from signal generation. No position may cross a data
role or annual-fold boundary. Each trade belongs to its signal-date fold and must enter and exit
within that fold. Development, Historical, and Shadow sessions cannot overlap or be reassigned
after outcome inspection.

### Fixed candidate inventory and trial/source identities

`maximum_trials=6`. Every viewed outcome-relevant semantic definition consumes one slot; rerunning
the exact same frozen fingerprint adds an observation but not a new trial. No seventh semantic
trial is permitted.

| Stable identity | Role | Frozen difference |
| --- | --- | --- |
| `xlf-rate-volatility-conditioned-pullback-gap-safe/move-direction-cap-3` | selection candidate | MOVE three-decision-session change <= +3 |
| `xlf-rate-volatility-conditioned-pullback-gap-safe/move-direction-cap-5` | selection candidate | MOVE three-decision-session change <= +5 |
| `xlf-rate-volatility-conditioned-pullback-gap-safe/move-direction-cap-7` | selection candidate | MOVE three-decision-session change <= +7 |
| `xlf-rate-volatility-conditioned-pullback-gap-safe/ungated-pullback-baseline` | distinct simple baseline | same XLF pullback/execution, no auxiliary gate |
| `xlf-rate-volatility-conditioned-pullback-gap-safe/selected-cap-minus-one-robustness` | robustness only | selected cap minus one MOVE point |
| `xlf-rate-volatility-conditioned-pullback-gap-safe/selected-entry-lag-two-robustness` | robustness only | selected cap with entry delayed to the second next open |

The first four identities have permanent source entry points under
`src/trading/research_definitions/xlf-rate-volatility-conditioned-pullback-gap-safe/`. The two
robustness identities are deterministic reserved identities: they may be materialized only after
Development selects one cap, must use the same gap-safe runtime and exact policy set, cannot enter
the candidate ranking, and must match the frozen transformations above. Every formal observation
requires a newly captured immutable Research Definition Snapshot containing exact source bytes;
no existing v003 snapshot or result may substitute for it.

### Frozen signal, execution, costs, and sleeve assumptions

- Signal after completed session `t`: XLF close <= its 20-session mean minus 2.0 sample standard
  deviations and its ten-session adjusted-close return <= -4%.
- A gated candidate additionally requires the gap-safe backward-as-of MOVE close change over
  three decision sessions <= its frozen cap and `ObservationAvailable=true`.
- Entry is market at the next XNYS open (`t+1`); delayed-entry robustness uses `t+2`. Exit is market
  at the XNYS open ten completed sessions after entry. There is no target, stop, trailing stop,
  limit entry, or intrabar trigger.
- Missing or non-finite next-open evidence is unfilled/integrity failure, never an inferred fill.
- Canonical isolated sleeve: normalized capital 1.0, fractional quantity, one open position,
  no leverage, pyramiding, cross-sleeve borrowing, rebalancing, or capital transfer. Overlapping
  candidates remain raw evidence and are canonically skipped as `position_already_open`.
- Gross candidates contain no embedded costs. Base costs are 5 bps entry slippage, 5 bps exit
  slippage, and 1 bps fee per side. Strictly adverse stress costs are 20 bps entry slippage,
  20 bps exit slippage, and 2 bps fee per side, exactly as pinned by
  `canonical-execution@v001`.

## Method and stages

### 1. Preregistration

Validate the released workflow and four policy pins, exact lineage, source identities, fixed data
roles, unavailable inventory, trial budget, selection rule, costs, gates, and human approval.
Generate `PREREGISTRATION.json` before any v004 refresh, snapshot, Research Definition Snapshot,
formal run, metric calculation, candidate ranking, candidate freeze, or Development/Historical/
Shadow outcome inspection. After preregistration, this HYPOTHESIS and PLAN are immutable.

### 2. Development and candidate selection

This stage requires separate human authorization. Then, and only then, perform one full refresh of
XLF and MOVE through 2020-12-31 for the first candidate; the remaining candidates and baseline must
reuse that exact eligible full-refresh generation without provider access. Before any strategy
output, verify all four manifests, one identical XLF blob across the family, one identical MOVE
blob across the three gated candidates, exact `mark_unavailable` manifest binding, the three-date
unavailable inventory, and complete signal-suppression proof.

Run all three candidates and the baseline offline using only Development-eligible sessions. Do not
calculate, display, serialize into the Development decision, or use any 2021–2025 outcome.

A candidate is Development-eligible only with at least 30 completed base-net trades across at
least ten traded calendar years, base compounded return > 0, base profit factor > 1.1, stress
compounded return > 0, stress profit factor > 1.0, stress maximum drawdown <= 15%, exact
unavailable-decision suppression, and no unresolved policy/provenance/parity/integrity difference.
It must also exceed the ungated baseline by at least 0.25 base-net daily-equity Sharpe.

Exclude ineligible candidates, then rank every remaining candidate by base-net daily-equity Sharpe
descending; exact ties use cap-3, cap-5, cap-7 stable identity order. If any required candidate or
baseline is invalid, stop without partial ranking. If none is eligible, record the no-candidate
outcome as `fail`. Persist the complete set and rationale, materialize the two deterministic
robustness identities, and obtain human owner approval before candidate freeze or Historical
access.

### 3. Historical Evaluation and robustness

After separately approved candidate freeze, evaluate only the frozen selected candidate, distinct
baseline, and two robustness definitions on five annual folds for 2021–2025. Recompute gross,
base-net, and stress-net outcomes under the canonical sleeve and record zero-signal folds plus the
chained five-fold capital path.

Required challenges are cash; the distinct ungated baseline; 1,000 exposure-matched random-entry
replicas using seed `20260812`; a family-wise 20-session block bootstrap over all three selection
candidates with 1,000 replicas and the same seed; cap-minus-one; delayed entry; stress/worse fills;
deterministic omission of 10% of otherwise executable entries with the same seed; and annual
market-regime evidence. Challenges may falsify the candidate but cannot replace or rerank it.

Viewing any 2021–2025 outcome consumes those folds for this round. A Historical failure terminates
the round; a modified candidate cannot reuse those folds as validation.

### 4. Prospective Shadow and later stages

Only a persisted passing Historical screen permits current-time prospective Shadow registration.
No preregistration-era or pre-registration 2026 session may be backfilled. Shadow remains
non-actionable paper proposals and canonical simulated fills for at least 252 completed sessions
and 12 completed fills. Activation and monitoring require all separate v004 lifecycle, ledger,
reconciliation, allocation, data-parity, drift, and no-new-entry controls. This study never grants
broker or live-order authority.

## Metrics and outcome rules

Historical gates are conjunctive:

- five complete, consecutive, non-overlapping annual folds;
- at least 20 completed Historical trades, at least three traded folds, and at least 60% positive
  traded folds;
- chained base compounded return > 0 and base profit factor > 1.1;
- chained stress compounded return > 0 and stress profit factor > 1.0;
- stress maximum drawdown <= 15%;
- no fold contributes more than 50% of total completed trades or total positive profit;
- selected candidate base-net daily-equity Sharpe exceeds the ungated baseline by at least 0.25;
- selected candidate compounded return exceeds cash, the ungated baseline, and the 90th percentile
  exposure-matched random-entry return;
- family-wise block-bootstrap selection confidence >= 90%;
- cap-minus-one, delayed-entry, stress/worse-fill, missed-entry, and annual-regime challenges show
  no non-positive stress return, stress profit factor <= 1.0, stress drawdown > 15%, unavailable-
  decision leakage, unresolved integrity difference, or reversal of the claimed MOVE direction.

Outcomes follow the pinned workflow:

- `pass`: every required Development/Historical identity and gate is complete and passing. A
  Historical pass grants only `shadow-eligible`.
- `fail`: a complete Development or Historical gate fails, no Development candidate qualifies,
  or the six-trial budget is exhausted.
- `insufficient-evidence`: only an open prospective Shadow checkpoint allowed by v004, chiefly
  when minimum duration has elapsed but completed fills remain below 12.
- `indeterminate`: any required identity, source byte, data, policy pin, unavailable inventory,
  suppression proof, provenance, replay, approval, or gate evidence is missing, stale, corrupt,
  conflicting, or unverifiable. Advancement stops; partial ranking is prohibited.

Shadow must independently satisfy at least 252 completed sessions and 12 fills, positive base and
stress returns, base and stress profit factors > 1.0, stress drawdown <= 15%, and the critical-drift
requirements. Shadow pass grants only `activation-eligible`.

## Deviations and stopping rules

After preregistration, do not change the hypothesis, data roles or dates, candidate inventory,
trial budget, source identities, signal formula, MOVE publication/maximum lag, `mark_unavailable`
semantics or three-date inventory, selection rule, baseline, costs, execution, purge/embargo,
thresholds, seeds, gates, or outcome rules. A necessary design change requires cancellation and a
new CLI-allocated study with an exact `revisits` path; it cannot repair this study retrospectively.

Pause advancement on incomplete or stale market data, unequal common-series blobs, release digest
drift, missing exact source bytes, invalid manifest, unavailable-inventory mismatch, suppression
failure, provenance/parity mismatch, partial candidate availability, or any v004 fail-closed
condition. Record deviations append-only in EVIDENCE; never hide a trial, expand the budget,
loosen a lag/cap/gate, change an unavailable session after outcome access, replace immutable
evidence with mutable `latest`, or use Historical/Shadow outcomes to redesign candidates.

Terminate the round when no Development candidate is eligible, the trial budget is exhausted, a
Historical or Shadow gate fails, a frozen definition changes materially, required evidence cannot
be recovered, or the human owner stops the study. Formal execution, data refresh, snapshots,
candidate freeze, outcome inspection, broker access, orders, and live authorization remain outside
this preregistration authorization and require separate explicit approval.
