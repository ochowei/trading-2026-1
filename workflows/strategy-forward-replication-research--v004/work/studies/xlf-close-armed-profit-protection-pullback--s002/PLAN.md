# Plan: XLF Close-Armed Profit-Protection Pullback Research

## Inputs and frozen identities

### Governance, lineage, and authority

- Study: `strategy-forward-replication-research@v004/S002` at
  `workflows/strategy-forward-replication-research--v004/work/studies/xlf-close-armed-profit-protection-pullback--s002`.
- Workflow: `strategy-forward-replication-research@v004` at
  `workflows/strategy-forward-replication-research--v004`.
- Exact predecessor and `revisits` identity:
  `workflows/strategy-forward-replication-research--v004/work/studies/xlf-rate-volatility-conditioned-pullback-gap-safe--s001`.
- Workflow `RELEASE.json` SHA-256:
  `5e00e3ed5b4d87de39f4db48ac5a523cdb82992b737a5306e8928a4073320430`.
- Workflow definition SHA-256:
  `d176471dd099bf55274748d82957cd5a410b40ddda5e38c9e8d69926a66431da`.
- Canonical source Git HEAD at draft preparation:
  `ef1713123d4063268221ac53a7f44b117befff5e`.
- Composite policy set:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Human research owner and future preregistration/candidate-freeze approver:
  `ochowei@gmail.com`.
- Researcher identity: `codex-primary-researcher-xlf-profit-protection`.

The planning-stage blind contamination audit found no S001 candidate-freeze artifact, Historical
run, Historical result, Historical metric, Shadow registration, Shadow fill, or corresponding XLF
S001 result artifact. It found an explicit Development-only stop. This audit disclosed no
Historical or Shadow outcome. Before preregistration, deterministic validation must repeat the
artifact-presence audit. Any contrary evidence requires stopping this draft and assigning new,
unconsumed data roles before preregistration.

### Released policy pins

| Family | Version | `RELEASE.json` SHA-256 |
| --- | --- | --- |
| `us-equity-market` | `v002` | `9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` |

No implicit `latest` policy is permitted. Every formal Research Definition Snapshot and result
must bind this exact composite set and v004 release.

### Market data and frozen data roles

- Sole market-data dependency: Yahoo auto-adjusted daily OHLCV for `XLF`, with complete
  XNYS-session coverage required from 2002-11-13.
- There is no MOVE or other auxiliary series, no auxiliary availability decision, and no
  `mark_unavailable` behavior in this family.

| Role | Frozen completed sessions |
| --- | --- |
| Warmup only | 2002-11-13 through 2003-12-31 |
| Development | 2004-01-02 through 2020-12-31 |
| Historical Evaluation | Five annual folds: 2021, 2022, 2023, 2024, and 2025 |
| Quarantined | All 2026 sessions before any future current-time Shadow registration |
| Shadow | Prospective sessions only after a persisted passing Historical screen and registration |

For each Development/Historical segment, the first 21 completed primary sessions are warmup-only
and the final 11 primary sessions are purged from signal generation. A trade belongs to its signal
date fold, must enter and exit within that fold, and cannot cross a data role. No session may be
reassigned after outcome inspection.

### Fixed candidate inventory and intended source identities

`maximum_trials=5`. Every viewed outcome-relevant semantic definition consumes one slot; rerunning
the exact same fingerprint adds an observation but not a trial. No sixth semantic trial is allowed.

| Stable identity | Role | Frozen difference |
| --- | --- | --- |
| `xlf-close-armed-profit-protection-pullback/close-armed-2-floor-0p5` | sole selection candidate | arm at +2.0%; later close at or below +0.5% exits next open |
| `xlf-close-armed-profit-protection-pullback/fixed-ten-session-baseline` | distinct simple baseline | identical entry and occupation lock; fixed ten-session exit only |
| `xlf-close-armed-profit-protection-pullback/arm-1p5-floor-0p5-robustness` | robustness only | arm at +1.5%; floor remains +0.5% |
| `xlf-close-armed-profit-protection-pullback/arm-2p5-floor-0p5-robustness` | robustness only | arm at +2.5%; floor remains +0.5% |
| `xlf-close-armed-profit-protection-pullback/delayed-protection-exit-robustness` | robustness only | selected trigger; protection exit delayed one additional completed session |

The five identities have permanent source entry points under
`src/trading/research_definitions/xlf-close-armed-profit-protection-pullback/`. The three robustness
source identities exist before preregistration so their exact bytes can be reviewed and pinned, but
their formal snapshots and observations may be materialized only after Development selects the
sole candidate. They cannot enter ranking or replace it. Implementing and provider-free validating
these source bytes is a preregistration-readiness action; formal snapshot or outcome execution is
not authorized by this draft alone.

No source or result from S001 may substitute for a new immutable Research Definition Snapshot.
The entry formula may be implemented through shared maintained runtime code, but each formal
identity must capture exact source, detector, backtester, resolved config, policy set, runtime, and
dependency bytes.

### Frozen signal, state machine, execution, and sleeve

- Signal after completed session `t`: XLF adjusted close is at or below its 20-session mean minus
  2.0 sample standard deviations and its ten-session adjusted-close return is at or below -4%.
- Entry is market at the next XNYS open (`t+1`). Missing or non-finite open evidence is unfilled or
  an integrity failure, never an inferred fill.
- The observed adjusted entry open, before any cost overlay, is the immutable state reference.
  Trigger state is therefore identical under gross, base, and stress cost calculations.
- The candidate is initially `unarmed`. Starting with the entry session close, a completed close
  at or above 102.0% of the state reference permanently changes it to `armed`.
- Only a strictly later completed close can fire protection. Once armed, the first completed close
  at or below 100.5% of the state reference schedules market exit at the next XNYS open.
- If protection never fires, exit is market at the open ten completed sessions after entry, exactly
  as in S001's baseline. If a protection decision and time-expiry decision schedule the same open,
  use the same price and classify the exit as `time_expiry`; only a strictly earlier exit counts as
  protection engagement. This preserves canonical expiry-before-entry event ordering.
- The +0.5% floor is fixed to entry. It does not trail the running high. There is no target, hard
  stop, intrabar trigger, limit order, same-close fill, or adverse-persistence candidate.
- Candidate and baseline use a ten-session occupation lock beginning at entry. A candidate that
  exits early remains ineligible for a new entry until the open at which its matched baseline would
  expire. Intervening raw signals are recorded and skipped as `occupation_lock`; this prevents
  early-exit capital release from changing the accepted-entry cohort.
- Candidate and baseline must expose identical raw signals and identical accepted entry dates.
  Any mismatch is an integrity failure and stops comparison as `indeterminate`.
- Canonical isolated sleeve: normalized capital 1.0, fractional quantity, one economic occupation
  at a time, no leverage, pyramiding, cross-sleeve borrowing, rebalancing, or capital transfer.
  Cash after an early candidate exit earns zero and remains locked until matched baseline expiry.

### Costs and deterministic challenges

- Gross candidates contain no embedded costs.
- Base costs: 5 bps entry slippage, 5 bps exit slippage, and 1 bp fee per side.
- Strictly adverse stress costs: 20 bps entry slippage, 20 bps exit slippage, and 2 bps fee per side.
- Protection decisions use the observed adjusted open/close state, not cost-adjusted synthetic
  prices; costs affect realized returns only.
- Exposure-matched random entries, the 20-session family-wise block bootstrap, and deterministic
  omission of 10% of otherwise executable entries each use seed `20260813` and 1,000 replicas where
  replication applies.

## Method and stages

### 1. Draft completion and preregistration readiness

This study remains `draft`. Before asking for preregistration approval, provider-free validate the
five exact workflow-native identities, verify the active v004 release and four policy pins, repeat
the blind S001 contamination audit, verify the source/data declarations and trial inventory, and
show the complete frozen summary to the human owner. No data refresh, snapshot, formal run, metric,
ranking, candidate freeze, Historical access, or Shadow access is authorized during drafting.

Only explicit approval with a stable human identity may authorize the separate CLI
`workflow study preregister` action. After preregistration, this HYPOTHESIS and PLAN are immutable.

### 2. Development and candidate selection

Development execution requires separate human authorization after preregistration. Perform one
authoritative full refresh of XLF through 2020-12-31 for the first identity; every other identity
must reuse the same eligible full-refresh generation without provider access. Before inspecting
strategy output, verify exact policy/provenance bindings, common XLF blob identity, source bytes,
purge/embargo, occupation-lock parity, and observation provenance.

Run the sole candidate and distinct baseline offline using only Development-eligible sessions.
The robustness identities are not candidates and cannot enter selection. Because the candidate set
contains exactly one identity, the v004 ranking rule is deterministic: exclude it if ineligible;
otherwise rank and select that single candidate. There is no parameter or cohort competition.

Development eligibility is conjunctive:

- at least 30 completed trades across at least ten traded calendar years;
- at least ten `profit_protection` exits across at least five calendar years;
- base compounded return > 0 and base profit factor > 1.1;
- stress compounded return > 0, stress profit factor > 1.0, and stress maximum drawdown <= 15%;
- candidate base compounded return >= 90% of baseline base compounded return;
- candidate base-net daily-equity Sharpe >= baseline plus 0.10;
- candidate stress maximum drawdown <= 85% of baseline stress maximum drawdown;
- aggregate paired base-net advantage on protection-fired trades versus their matched baseline
  expiry returns > 0;
- identical raw signals and accepted-entry cohort, exact occupation-lock parity, and no unresolved
  source, policy, provenance, replay, cost, execution, or integrity difference.

If any condition fails, record `fail`; do not tune a threshold or substitute a robustness identity.
If eligible, persist the complete comparison and rationale, materialize the three deterministic
robustness identities, and obtain separate human candidate-freeze approval before Historical
access.

### 3. Historical Evaluation and robustness

After approved candidate freeze, evaluate only the frozen candidate, distinct baseline, and three
robustness definitions on the five annual 2021-2025 folds. Recompute gross, base-net, and stress-net
outcomes under the canonical sleeve, including zero-signal folds and the chained five-fold capital
path.

Required challenges are cash; the distinct baseline; 1,000 exposure-matched random-entry replicas;
the family-wise 20-session block bootstrap over the one-candidate family with 1,000 replicas; both
arming perturbations; the delayed protection exit; stress/worse fills; deterministic omission of
10% of executable entries; and annual market-regime evidence. Challenges only falsify or support
the candidate and cannot replace or rerank it.

Viewing any 2021-2025 outcome consumes those folds for this round. A Historical failure terminates
the round, and a modified candidate cannot reuse the folds as validation.

### 4. Prospective Shadow and later stages

Only a persisted passing Historical screen permits current-time prospective Shadow registration.
No preregistration-era or pre-registration 2026 session may be backfilled. Shadow is non-actionable
paper proposals and canonical simulated fills for at least 252 completed sessions and 12 completed
fills. Activation and monitoring require every separate v004 lifecycle, ledger, reconciliation,
allocation, data-parity, drift, and no-new-entry control. This study grants no broker or live-order
authority.

## Metrics and outcome rules

Historical gates are conjunctive:

- five complete, consecutive, non-overlapping annual folds;
- at least 20 completed trades, at least three traded folds, and at least 60% positive traded folds;
- at least five protection exits across at least three annual folds;
- chained base compounded return > 0 and base profit factor > 1.1;
- chained stress compounded return > 0, stress profit factor > 1.0, and stress drawdown <= 15%;
- no fold contributes more than 50% of total trades or total positive profit;
- candidate base compounded return >= 90% of baseline;
- candidate base-net daily-equity Sharpe >= baseline plus 0.10;
- candidate stress maximum drawdown <= 85% of baseline stress maximum drawdown;
- paired protection-exit advantage is positive in at least 60% of folds containing such an exit;
- candidate compounded return exceeds cash and the 90th percentile exposure-matched random return;
- family-wise block-bootstrap selection confidence >= 90%;
- both arming perturbations and delayed-exit, stress/worse-fill, missed-entry, occupation-lock, and
  annual-regime challenges retain positive stress return, stress profit factor > 1.0, stress
  drawdown <= 15%, base return >= 90% of baseline, Sharpe above baseline, and stress drawdown below
  baseline, without an integrity difference or claim-direction reversal.

Outcomes follow v004:

- `pass`: every required Development/Historical identity and gate is complete and passing. It
  grants only `shadow-eligible`.
- `fail`: a complete Development or Historical gate fails, the sole candidate is ineligible, the
  protection mechanism is non-binding, a robustness challenge reverses the claim, or the five-trial
  budget is exhausted.
- `insufficient-evidence`: only an open prospective Shadow checkpoint allowed by v004, chiefly
  when minimum duration has elapsed but completed fills remain below 12.
- `indeterminate`: any required identity, source byte, data, policy pin, provenance, replay,
  approval, cohort parity, occupation lock, or gate evidence is missing, stale, corrupt,
  conflicting, or unverifiable. Advancement stops and partial evidence cannot support selection.

Shadow must independently satisfy at least 252 completed sessions and 12 fills, positive base and
stress returns, base and stress profit factors > 1.0, stress drawdown <= 15%, and every critical
drift requirement. Shadow pass grants only `activation-eligible`.

## Deviations and stopping rules

After preregistration, do not change the claim, data roles, dates, source identities, trial budget,
signal, entry, arm, floor, state transition, occupation lock, baseline, costs, execution timing,
purge/embargo, seeds, thresholds, challenges, or outcome rules. Do not add MOVE or any auxiliary
gate, choose h4/h6/h8 or another holding cohort, tune from S001 postmortem evidence, introduce an
adverse-persistence replacement, or let a robustness identity become the candidate.

Any outcome-relevant design change requires cancellation and a new CLI-allocated study with an
exact `revisits` path. It cannot repair S002 retrospectively. Pause advancement on incomplete or
stale data, unequal common-series blobs, source or release digest drift, missing exact bytes,
cohort/occupation-lock mismatch, invalid manifest, provenance/replay failure, partial trial
availability, or any v004 fail-closed condition.

Terminate the round when the candidate is Development-ineligible, the trial budget is exhausted,
a Historical or Shadow gate fails, a frozen definition changes materially, required evidence
cannot be recovered, or the human owner stops the study. Formal execution, refresh, snapshot,
candidate freeze, outcome inspection, broker access, orders, and live authorization all require
their own later approvals and are not authorized by this draft.
