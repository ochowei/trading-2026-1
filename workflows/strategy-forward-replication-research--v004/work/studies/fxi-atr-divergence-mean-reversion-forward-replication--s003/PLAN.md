# Plan: FXI ATR-Divergence Mean-Reversion Forward Replication

## Inputs and frozen identities

### Governance, lineage, and authority

- Study: `strategy-forward-replication-research@v004/S003` at
  `workflows/strategy-forward-replication-research--v004/work/studies/fxi-atr-divergence-mean-reversion-forward-replication--s003`.
- Workflow: `strategy-forward-replication-research@v004` at
  `workflows/strategy-forward-replication-research--v004`.
- Workflow `RELEASE.json` SHA-256:
  `5e00e3ed5b4d87de39f4db48ac5a523cdb82992b737a5306e8928a4073320430`.
- Workflow definition SHA-256:
  `d176471dd099bf55274748d82957cd5a410b40ddda5e38c9e8d69926a66431da`.
- Canonical source Git HEAD at draft preparation:
  `10bec55a4756e0606adc72447b6ca42dd819397c`.
- Composite policy set:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Human research owner and future preregistration/candidate-freeze approver:
  `ochowei@gmail.com`.
- Researcher identity: `codex-primary-researcher-fxi-mean-reversion`.
- `revisits: null`; no prior workflow-native FXI study exists in repository history.

Legacy FXI observations through 2025-12-31 are explicitly treated as contaminated Development
context because their selection history is incomplete. None may be relabeled as Historical,
Shadow, or formal qualification evidence. Before preregistration, repeat a repository-wide
artifact audit; contrary evidence can only make the boundary stricter.

### Released policy pins

| Family | Version | `RELEASE.json` SHA-256 |
| --- | --- | --- |
| `us-equity-market` | `v002` | `9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` |

No implicit `latest` policy is permitted. Every formal Research Definition Snapshot and result
must bind this exact composite set and v004 release.

### Market data, auxiliary availability, and frozen data roles

- Primary dependency: Yahoo auto-adjusted daily OHLCV for `FXI`.
- Auxiliary dependency: Yahoo auto-adjusted daily OHLCV for `ASHR`.
- Both series use completed XNYS-session observations. `ASHR` publication lag is zero completed
  sessions and maximum observation lag is zero: the same completed session must exist in both
  bundles before a signal can be evaluated.
- Auxiliary excess-lag mode is whole-bundle `fail`. `mark_unavailable`, backward-as-of
  substitution, forward fill, silent row removal, and signal production from an unavailable
  decision are prohibited.

| Role | Frozen completed sessions |
| --- | --- |
| Warmup only | 2013-11-06 through 2014-12-31, constrained by `ASHR` inception and verified coverage |
| Development | 2015-01-02 through 2025-12-31 |
| Quarantined | Every 2026 session before preregistration and all sessions not assigned below |
| Historical Evaluation | Five consecutive prospective annual folds: 2027, 2028, 2029, 2030, 2031 |
| Shadow | Prospective sessions only after a persisted passing Historical screen and current-time registration |

For each Development/Historical segment, the first 21 common completed sessions are warmup-only
and the final 21 common sessions are purged from signal generation. A trade belongs to its signal
date fold, must enter and exit within that fold, and cannot cross a data role. No session may be
reassigned after outcome inspection. If verified ASHR inception or coverage makes the stated
warmup unavailable, preregistration must stop; dates cannot be silently shifted.

### Fixed candidate inventory and intended source identities

`maximum_trials=6`. Every viewed outcome-relevant semantic definition consumes one slot; rerunning
the exact same fingerprint adds an observation but not a trial. No seventh semantic trial is
allowed.

| Stable identity | Role | Frozen difference |
| --- | --- | --- |
| `fxi-atr-divergence-mean-reversion/atr-band-ashr-divergence` | sole selection candidate | all seven entry gates; ASHR 20-session relative-return floor -8% |
| `fxi-atr-divergence-mean-reversion/pullback-wr-baseline` | distinct simple baseline | 5%-12% ten-session pullback and WR(10)<=-80 only; identical exits |
| `fxi-atr-divergence-mean-reversion/ashr-floor-minus-7-robustness` | robustness only | candidate with ASHR floor -7% |
| `fxi-atr-divergence-mean-reversion/ashr-floor-minus-9-robustness` | robustness only | candidate with ASHR floor -9% |
| `fxi-atr-divergence-mean-reversion/atr-ceiling-1p30-robustness` | robustness only | candidate with ATR ratio ceiling 1.30 |
| `fxi-atr-divergence-mean-reversion/hold-18-robustness` | robustness only | candidate with eighteen-session maximum holding |

The six permanent source entry points must be implemented under
`src/trading/research_definitions/fxi-atr-divergence-mean-reversion/` and provider-free validated
before preregistration. Legacy source may inform an independent implementation but cannot be
imported as the formal identity or substituted for a new immutable Research Definition Snapshot.
The four robustness identities exist before preregistration for byte review but may be formally
executed only after the sole candidate passes Development and receives candidate-freeze approval.
They cannot enter ranking or replace the candidate.

### Frozen signal, execution, cooldown, and sleeve

- On completed session `t`, `High_N` is the maximum adjusted high over the inclusive last ten
  common sessions, and `Pullback=(adjusted_close-High_N)/High_N` must be between -12% and -5%,
  inclusive.
- Williams %R(10) uses inclusive rolling adjusted high/low and must be <= -80. A zero range is
  assigned -50 and cannot pass.
- `ClosePos=(adjusted_close-adjusted_low)/(adjusted_high-adjusted_low)` must be >= 0.40. A zero
  range is assigned 0.50.
- True range is the maximum of high-low, absolute high-prior-close, and absolute low-prior-close.
  Simple rolling ATR(5)/ATR(20) must be > 1.05 and <= 1.35.
- `Rel_Return` is `FXI` twenty-common-session adjusted-close return minus `ASHR`
  twenty-common-session adjusted-close return and must be >= -8%.
- Accepted signals use a ten-completed-session cooldown measured from the last accepted signal;
  a gap of ten or fewer completed sessions is suppressed and recorded.
- Entry is market at the next XNYS open. The target is a +5.5% Day limit order, the stop is a
  -5.0% GTC stop-market, and both are active from the entry session after the entry event.
  Unresolved positions expire at the open after twenty completed sessions strictly after entry.
  Same-session target/stop ambiguity uses the pinned pessimistic ordering. Missing or non-finite
  prices never create inferred fills.
- Canonical isolated sleeve: normalized capital 1.0, fractional quantity, one position at a time,
  no leverage, pyramiding, cross-sleeve borrowing, rebalancing, or capital transfer.

### Costs and deterministic challenges

- Gross definitions contain no embedded costs.
- Base costs: 5 bps entry slippage, 5 bps exit slippage, and 1 bp fee per side.
- Strictly adverse stress costs: 20 bps entry slippage, 20 bps exit slippage, and 2 bps fee per side.
- Exposure-matched random entries, the twenty-session family-wise block bootstrap, and
  deterministic omission of 10% of otherwise executable entries each use seed `20260813` and
  1,000 replicas where replication applies.

## Method and stages

### 1. Draft completion and preregistration readiness

This study remains `draft`. Implement and provider-free validate the six workflow-native source
identities, verify active v004 and all policy pins, verify ASHR coverage/inception, repeat the
contamination audit, and show the complete frozen summary to the human owner. No refresh, snapshot,
formal run, metric, ranking, candidate freeze, Historical access, or Shadow access is authorized
during drafting.

Only explicit approval with a stable human identity may authorize the separate CLI
`workflow study preregister` action. After preregistration, this HYPOTHESIS and PLAN are immutable.

### 2. Development and candidate selection

Development execution requires separate human authorization after preregistration. Perform one
authoritative full refresh of FXI and ASHR through 2025-12-31 for the first identity; every other
identity must reuse the same eligible full-refresh generation without provider access. Before
strategy-output inspection, verify exact policy/provenance bindings, common bundle identity,
source bytes, purge/embargo, cooldown behavior, and observation provenance.

Run only the sole candidate and distinct baseline on Development. The v004 selection rule is
deterministic: exclude the candidate if ineligible; otherwise select that single candidate.
Development eligibility is conjunctive:

- at least 30 completed trades across at least ten traded calendar years;
- base compounded return > 0 and base profit factor > 1.1;
- stress compounded return > 0, stress profit factor > 1.0, and stress drawdown <= 20%;
- candidate base return >= 90% of baseline, Sharpe >= baseline plus 0.10, and stress drawdown no
  worse than baseline;
- both ATR ceiling and ASHR gate each uniquely suppress at least ten baseline-eligible entries
  across at least five Development calendar years;
- exact source, data, auxiliary availability, cost, execution, replay, and provenance integrity.

If any condition fails, record `fail`; do not tune a threshold or promote a robustness identity.
If eligible, persist the complete comparison and obtain separate human candidate-freeze approval
before any 2027-2031 outcome access.

### 3. Historical Evaluation and robustness

After approved candidate freeze and only after 2031 is complete, evaluate the frozen candidate,
baseline, and four robustness identities on the five annual 2027-2031 folds. Recompute gross,
base-net, and stress-net outcomes under the canonical sleeve, including zero-signal folds and the
chained capital path.

Required challenges are cash; the distinct baseline; 1,000 exposure-matched random-entry
replicas; the twenty-session family-wise block bootstrap over the one-candidate family with 1,000
replicas; both ASHR-floor perturbations; ATR-ceiling and holding perturbations; stress/worse fills;
deterministic omission of 10% of executable entries; and annual China-equity regime evidence.
Challenges only falsify or support the candidate and cannot replace or rerank it.

Viewing any 2027-2031 outcome consumes those folds for this round. Historical failure terminates
the round, and a modified candidate cannot reuse the folds as validation.

### 4. Prospective Shadow and later stages

Only a persisted passing Historical screen permits current-time prospective Shadow registration.
No prior session may be backfilled. Shadow is non-actionable paper proposals and canonical
simulated fills for at least 252 completed sessions and 12 completed fills. Activation and
monitoring require every separate v004 lifecycle, ledger, reconciliation, allocation, data-parity,
drift, and no-new-entry control. This study grants no broker or live-order authority.

## Metrics and outcome rules

Historical gates are conjunctive:

- five complete, consecutive, non-overlapping annual folds;
- at least 20 completed trades, at least three traded folds, and at least 60% positive traded folds;
- chained base return > 0 and profit factor > 1.1;
- chained stress return > 0, profit factor > 1.0, and drawdown <= 20%;
- no fold contributes more than 50% of total trades or total positive profit;
- candidate base return >= 90% of baseline, Sharpe >= baseline plus 0.10, and stress drawdown no
  worse than baseline;
- each compound filter uniquely suppresses at least five baseline-eligible entries across at least
  three folds;
- candidate return exceeds cash and the 90th percentile exposure-matched random return;
- family-wise block-bootstrap selection confidence >= 90%;
- all perturbation, cost/fill, missed-entry, cooldown, auxiliary-availability, and annual-regime
  challenges retain positive stress return, stress profit factor > 1.0, stress drawdown <= 20%,
  base return >= 90% of baseline, and Sharpe above baseline without a claim-direction reversal.

Outcomes follow v004:

- `pass`: every required identity and frozen Development/Historical gate is complete and passing;
  it grants only `shadow-eligible`.
- `fail`: a complete gate fails, the candidate is ineligible, either filter is non-binding, a
  robustness challenge reverses the claim, or the six-trial budget is exhausted.
- `insufficient-evidence`: only an open prospective Shadow checkpoint allowed by v004, chiefly
  when minimum duration has elapsed but completed fills remain below 12.
- `indeterminate`: any required identity, source byte, data, auxiliary availability, policy pin,
  provenance, replay, approval, or gate evidence is missing, stale, corrupt, conflicting, or
  unverifiable. Advancement stops and partial evidence cannot support selection.

Shadow must independently satisfy at least 252 completed sessions and 12 fills, positive base and
stress returns, base and stress profit factors > 1.0, stress drawdown <= 20%, and every critical
drift requirement. Shadow pass grants only `activation-eligible`.

## Deviations and stopping rules

After preregistration, do not change the claim, dates, data roles, source identities, trial budget,
signal formula, ASHR availability rule, cooldown, exits, baseline, costs, execution timing,
purge/embargo, seeds, thresholds, challenges, or outcome rules. Do not add or substitute a legacy
identity, CNY/VIX/EEM/trend/gap/BB-width filter, tune from 2027-2031 outcomes, or let a robustness
identity become the candidate.

Any outcome-relevant design change requires cancellation and a new CLI-allocated study with an
exact `revisits` path. Pause advancement on incomplete or stale data, unequal common-series blobs,
source/release digest drift, missing exact bytes, invalid manifests, auxiliary availability error,
provenance/replay failure, or partial trial availability.

Terminate the round when the candidate is Development-ineligible, the trial budget is exhausted,
a Historical or Shadow gate fails, a frozen definition changes materially, required evidence
cannot be recovered, or the human owner stops the study. Formal execution, refresh, snapshot,
candidate freeze, outcome inspection, broker access, orders, and live authorization all require
their own later approvals and are not authorized by this draft.
