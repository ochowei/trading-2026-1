# Plan: FXI ATR-Band Mean-Reversion Forward Replication

## Inputs and frozen identities

### Governance, lineage, and authority

- Study: `strategy-forward-replication-research@v004/S004` at
  `workflows/strategy-forward-replication-research--v004/work/studies/fxi-atr-band-mean-reversion-forward-replication--s004`.
- Workflow: `strategy-forward-replication-research@v004` at
  `workflows/strategy-forward-replication-research--v004`.
- Exact `revisits` target:
  `workflows/strategy-forward-replication-research--v004/work/studies/fxi-atr-divergence-mean-reversion-forward-replication--s003`.
- Workflow `RELEASE.json` SHA-256:
  `5e00e3ed5b4d87de39f4db48ac5a523cdb82992b737a5306e8928a4073320430`.
- Workflow definition SHA-256:
  `d176471dd099bf55274748d82957cd5a410b40ddda5e38c9e8d69926a66431da`.
- Canonical source Git HEAD at draft preparation:
  `bb90cb5c4d05d38451f407aa749f37d6d429da08`.
- Composite policy set:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Human research owner and future preregistration/candidate-freeze approver:
  `ochowei@gmail.com`.
- Researcher identity: `codex-primary-researcher-fxi-mean-reversion`.

S003 is immutable and terminal `fail`. It may not be edited, revived, rerun, reinterpreted as a
pass, or granted a candidate freeze. All legacy and workflow-native FXI/ASHR observations viewed
through 2025-12-31 are explicitly Development context because they influenced this round and their
full legacy selection history is incomplete. No such observation may be relabeled as Historical,
Shadow, or formal qualification evidence.

The repository freshness audit on 2026-08-13 reports the 2025-12-31 knowledge cutoff as older than
six months. That is a warning, not authority to refresh. Before any later preregistration, repeat a
repository-wide contamination, freshness, trial-history, and source-identity audit. Contrary
evidence can only make the boundary stricter.

### Released policy pins

| Family | Version | `RELEASE.json` SHA-256 |
| --- | --- | --- |
| `us-equity-market` | `v002` | `9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` |

The root registry and deterministic CLI validation on 2026-08-13 identify v004 as the unique
active released workflow, and all four policy release digests validate. No implicit `latest`
workflow or policy is permitted. Every formal Research Definition Snapshot and result must bind
this exact v004 release and composite policy set.

### Market data, freshness, and frozen data roles

- Sole market-data dependency: Yahoo auto-adjusted daily OHLCV for `FXI`.
- The candidate has no auxiliary series. `ASHR`, CNY, EEM, VIX, and other cross-asset data are not
  inputs, fallback sources, availability gates, or robustness dimensions in this round.
- Only completed XNYS-session observations may be used. Missing, duplicate, non-finite, stale, or
  session-invalid primary data makes the bundle fail closed.
- S003 established that an immutable FXI bundle through 2025-12-31 was available, but this draft
  does not reuse, refresh, snapshot, inspect, or execute it. Any later formal data action requires
  separate authority and exact v004 provenance.

| Role | Frozen completed sessions |
| --- | --- |
| Warmup only | 2013-11-06 through 2014-12-31; observations may initialize indicators only |
| Development | 2015-01-02 through 2025-12-31 |
| Quarantined | Every 2026 session and every session not explicitly assigned below |
| Historical Evaluation | Five consecutive prospective annual folds: 2027, 2028, 2029, 2030, 2031 |
| Shadow | Prospective sessions only after a persisted passing Historical screen and current-time registration |

For Development and every Historical fold, the first 21 completed sessions are dependency warmup
and embargo-only and the final 21 completed sessions are purged from signal generation. A trade
belongs to its signal-date fold, enters no earlier than the next completed XNYS session, and must
enter and exit within the same role and fold. Positions, signals, cooldown state, P&L, and capital
may not cross a role or fold boundary. Warmup observations may seed rolling indicators but never
performance, signals, fills, cooldown, or carry-in positions. No session may be reassigned after
outcome inspection.

### Fixed candidate inventory and intended source identities

`maximum_trials=6`. Every viewed outcome-relevant semantic definition consumes one slot; rerunning
the exact same fingerprint adds an observation but not a trial. No seventh semantic trial is
allowed.

| Stable identity | Role | Frozen difference |
| --- | --- | --- |
| `fxi-atr-band-mean-reversion/atr-band-candidate` | sole selection candidate | pullback, WR, ClosePos, and ATR ratio in `(1.05, 1.35]` |
| `fxi-atr-band-mean-reversion/pullback-wr-baseline` | distinct simple baseline | 5%-12% ten-session pullback and WR(10)<=-80 only; identical exits |
| `fxi-atr-band-mean-reversion/atr-floor-1p10-robustness` | robustness only | candidate with strict ATR-ratio floor 1.10 |
| `fxi-atr-band-mean-reversion/atr-ceiling-1p30-robustness` | robustness only | candidate with ATR-ratio ceiling 1.30 |
| `fxi-atr-band-mean-reversion/hold-18-robustness` | robustness only | candidate with eighteen-session maximum holding |
| `fxi-atr-band-mean-reversion/delay-one-session-robustness` | robustness only | candidate entry delayed one additional completed session |

Frozen source-byte inventory prepared before preregistration:

| Identity / runtime | SHA-256 |
| --- | --- |
| `atr-band-candidate/definition.py` | `a964aaf3e166becc24d4c66a9e00467bc77e05e8534da4b5b9ba6a0c4e67cc08` |
| `pullback-wr-baseline/definition.py` | `3a838b5460befdb37de57a6744339a2d0b1101d4972bd34a81da1bcde4fc2ba4` |
| `atr-floor-1p10-robustness/definition.py` | `1eb19a0ed7cae4ccdbbdd1d81ae4af99b8a5379b2c7de3296d9119d029bf015f` |
| `atr-ceiling-1p30-robustness/definition.py` | `499f034fc8f3bc0207f5e4bebae669d0c45624390e241499d95cb44f3f3a31ed` |
| `hold-18-robustness/definition.py` | `8b60508760f6b16c79d5aa7348e59fa0d21609e37f61c561750f10e62f869021` |
| `delay-one-session-robustness/definition.py` | `784f91d0b40b9f3a6b071cfe2cb08a8ba135631244ff0f5b08ec2e26c93d8df2` |
| shared `src/trading/research_definitions/fxi_mean_reversion.py` runtime | `120df54dde206dd16f6293bff7bf4f042b396d8970fd644458eadba677e2be7e` |

All six permanent source entry points are under
`src/trading/research_definitions/fxi-atr-band-mean-reversion/`. Provider-free registry loading,
definition capture against the exact v004 policy set, entry-delay semantics, and existing FXI
execution semantics passed the targeted test suite before preregistration. Any byte drift from
this inventory invalidates readiness and requires renewed human review before preregistration.

No package under `src/trading/experiments/` may be added, renamed, edited, or imported as the new
formal identity. The existing S003 research-definition family remains frozen provenance and may
inform an independent implementation, but it cannot be silently repurposed.

The four robustness identities must exist before preregistration for byte review but may be
formally executed only after the sole candidate passes Development and receives separate human
candidate-freeze approval. They cannot enter Development ranking, replace the candidate, or repair
a failure.

### Frozen signal, execution, cooldown, and sleeve

- On completed session `t`, `High_N` is the maximum adjusted high over the inclusive last ten
  completed FXI sessions. `Pullback=(adjusted_close-High_N)/High_N` must be between -12% and -5%,
  inclusive.
- Williams %R(10) uses inclusive rolling adjusted high/low and must be <= -80. A zero range is
  assigned -50 and cannot pass.
- `ClosePos=(adjusted_close-adjusted_low)/(adjusted_high-adjusted_low)` must be >= 0.40. A zero
  range is assigned 0.50.
- True range is the maximum of high-low, absolute high-prior-close, and absolute low-prior-close.
  Simple rolling `ATR(5)/ATR(20)` must be strictly greater than 1.05 and less than or equal to 1.35.
- Accepted signals use a ten-completed-session cooldown measured from the last accepted signal; a
  gap of ten or fewer completed sessions is suppressed and recorded.
- Entry is market at the next XNYS open. The target is a +5.5% Day limit order, the stop is a
  -5.0% GTC stop-market, and both become active after the entry event on the entry session.
  Unresolved positions expire at the open after twenty completed sessions strictly after entry.
  Same-session target/stop ambiguity uses the pinned pessimistic ordering. Missing or non-finite
  prices never create inferred fills.
- Canonical isolated sleeve: normalized capital 1.0, fractional quantity, one position at a time,
  no leverage, pyramiding, cross-sleeve borrowing, rebalancing, or capital transfer.

### Compound-filter binding definitions

Binding is measured before cooldown and occupation selection over valid core-baseline-eligible
decision sessions. Every counterfactual changes exactly one named gate while holding all other
candidate gates fixed:

- ATR-floor unique suppression: passes pullback, WR, ClosePos, and ATR ceiling, but has
  `ATR(5)/ATR(20) <= 1.05`.
- ATR-ceiling unique suppression: passes pullback, WR, ClosePos, and ATR floor, but has
  `ATR(5)/ATR(20) > 1.35`.
- Complete-band unique suppression: passes the pullback/WR baseline but fails one or both ATR-band
  sides while all indicator values are valid. ClosePos failure is excluded from this count.

Each decision session is counted once per applicable counterfactual, with the exact session and
calendar year/fold retained. These counts assess whether both stated volatility mechanisms can be
observed; they do not enter P&L, ranking, or threshold selection. The Development and Historical
minimum counts are frozen in `HYPOTHESIS.md` and the outcome rules below.

### Costs and deterministic challenges

- Gross definitions contain no embedded costs.
- Base costs: 5 bps entry slippage, 5 bps exit slippage, and 1 bp fee per side.
- Strictly adverse stress costs: 20 bps entry slippage, 20 bps exit slippage, and 2 bps fee per
  side.
- Exposure-matched random entries, the twenty-session family-wise block bootstrap, and
  deterministic omission of 10% of otherwise executable entries each use seed `20260813` and
  1,000 replicas where replication applies.

## Method and stages

### 1. Draft completion and preregistration readiness

This study remains `draft`. Before any request to preregister, independently implement and
provider-free validate the six workflow-native source identities, repeat the active-workflow and
policy-pin checks, verify source bytes and primary-only data declarations, and repeat the
contamination/freshness/trial-history audit. Show the complete frozen summary to the human owner.

No refresh, data-status outcome inspection, snapshot, formal run, metric, ranking, candidate
freeze, 2026 access, Historical access, Shadow access, broker access, or order is authorized during
drafting. Only explicit approval by `ochowei@gmail.com` in a later instruction may authorize the
separate CLI `workflow study preregister` action. After preregistration, this HYPOTHESIS and PLAN
are immutable.

### 2. Development and candidate selection

Development execution requires a second, separate human authorization after preregistration.
Perform one authoritative full refresh of FXI with an exact 2025-12-31 cutoff for the first
identity; every other identity must reuse the same eligible full-refresh generation without
provider access. Before strategy-output inspection, verify exact workflow, policy, source, data,
purge/embargo, cooldown, cost, execution, replay, and observation-provenance bindings.

Run only the sole candidate and distinct baseline on Development. The v004 selection rule is
deterministic: exclude the candidate if ineligible; otherwise select that single candidate.
Development eligibility is conjunctive:

- at least 30 completed trades across at least ten traded calendar years;
- base compounded return > 0 and base profit factor > 1.1;
- stress compounded return > 0, stress profit factor > 1.0, and stress drawdown <= 20%;
- candidate base return >= 90% of baseline, Sharpe >= baseline plus 0.10, and stress drawdown no
  worse than baseline;
- ATR floor uniquely suppresses at least five otherwise-candidate-eligible entries across at least
  three Development years, ATR ceiling independently does the same, and the complete ATR band
  uniquely suppresses at least ten core-baseline-eligible entries across at least five years;
- exact source, data, cost, execution, replay, trial-history, and provenance integrity.

If any condition fails, record evidence and stop for independent review; do not tune a threshold,
execute robustness trials, or freeze a candidate. If eligible, persist the complete comparison and
obtain separate explicit candidate-freeze approval from `ochowei@gmail.com` before any 2027-2031
outcome access.

### 3. Historical Evaluation and robustness

After approved candidate freeze and only after 2031 is complete, evaluate the frozen candidate,
baseline, and four robustness identities on the five annual 2027-2031 folds. Recompute gross,
base-net, and stress-net outcomes under the canonical sleeve, including zero-signal folds and the
chained capital path.

Required challenges are cash; the distinct baseline; 1,000 exposure-matched random-entry
replicas; the twenty-session family-wise block bootstrap over the complete six-trial family with
1,000 replicas; ATR-floor and ATR-ceiling perturbations; the eighteen-session holding and
one-session delayed-entry perturbations; stress costs/worse fills; deterministic omission of 10%
of executable entries; and annual China-equity regime evidence. Challenges only falsify or
support the candidate and cannot replace or rerank it.

Viewing any 2027-2031 outcome consumes those folds for this round. Historical failure terminates
the round, and a modified candidate cannot reuse the folds as validation.

### 4. Prospective Shadow and later stages

Only a persisted passing Historical screen permits current-time prospective Shadow registration.
No prior session may be backfilled. Shadow consists only of non-actionable paper proposals and
canonical simulated fills for at least 252 completed sessions and 12 completed fills. Activation
and monitoring require every separate v004 lifecycle, ledger, reconciliation, allocation,
data-parity, drift, and no-new-entry control. This study grants no broker or live-order authority.

## Metrics and outcome rules

Historical gates are conjunctive:

- five complete, consecutive, non-overlapping annual folds;
- at least 20 completed trades, at least three traded folds, and at least 60% positive traded
  folds;
- chained base return > 0 and profit factor > 1.1;
- chained stress return > 0, profit factor > 1.0, and drawdown <= 20%;
- no fold contributes more than 50% of total trades or total positive profit;
- candidate base return >= 90% of baseline, Sharpe >= baseline plus 0.10, and stress drawdown no
  worse than baseline;
- ATR floor and ATR ceiling each uniquely suppress at least two otherwise-candidate-eligible
  entries across at least two folds, and the complete ATR band uniquely suppresses at least five
  core-baseline-eligible entries across at least three folds;
- candidate return exceeds cash and the 90th percentile exposure-matched random return;
- family-wise block-bootstrap selection confidence >= 90%;
- all perturbation, cost/fill, missed-entry, cooldown, market-regime, and integrity challenges
  retain positive stress return, stress profit factor > 1.0, stress drawdown <= 20%, base return
  >= 90% of baseline, and Sharpe above baseline without a claim-direction reversal.

Outcomes follow v004:

- `pass`: every required identity and frozen Development/Historical gate is complete and passing;
  it grants only `shadow-eligible`.
- `fail`: a complete gate fails, the candidate is ineligible, either ATR-band side is non-binding,
  a robustness challenge reverses the claim, or the six-trial budget is exhausted.
- `insufficient-evidence`: only an open prospective Shadow checkpoint allowed by v004, chiefly
  when minimum duration has elapsed but completed fills remain below 12.
- `indeterminate`: any required identity, source byte, data, policy pin, provenance, replay,
  approval, or gate evidence is missing, stale, corrupt, conflicting, or unverifiable.
  Advancement stops and partial evidence cannot support selection.

Shadow must independently satisfy at least 252 completed sessions and 12 fills, positive base and
stress returns, base and stress profit factors > 1.0, stress drawdown <= 20%, and every critical
drift requirement. Shadow pass grants only `activation-eligible`.

## Deviations and stopping rules

After preregistration, do not change the claim, dates, data roles, source identities, trial budget,
signal formula, cooldown, exits, baseline, costs, execution timing, warmup, purge, embargo, seeds,
binding definitions, thresholds, challenges, or outcome rules. Do not add ASHR or substitute a
CNY/VIX/EEM/trend/gap/BB-width/oscillator filter, tune from 2026 or 2027-2031 outcomes, import a
legacy identity, or let a robustness identity become the candidate.

Any outcome-relevant design change requires cancellation and a new CLI-allocated study with an
exact `revisits` path. Pause advancement on incomplete or stale data, source/release digest drift,
missing exact bytes, invalid manifests, provenance/replay failure, hidden or partial trial
availability, policy mismatch, or any evidence that a quarantined/future outcome was inspected.

Terminate the round when the candidate is Development-ineligible, the trial budget is exhausted,
a Historical or Shadow gate fails, a frozen definition changes materially, required evidence
cannot be recovered, or the human owner stops the study. Formal execution, refresh, snapshot,
candidate freeze, 2026 or future outcome inspection, broker access, orders, and live authorization
all require their own later approvals and are not authorized by this draft.
