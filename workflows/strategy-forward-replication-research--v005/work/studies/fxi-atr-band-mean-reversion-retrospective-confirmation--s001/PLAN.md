# Plan: FXI ATR-Band Mean-Reversion Retrospective Confirmation

## Inputs and frozen identities

### Governance, lineage, and authority

- Study: `strategy-forward-replication-research@v005/S001` at
  `workflows/strategy-forward-replication-research--v005/work/studies/fxi-atr-band-mean-reversion-retrospective-confirmation--s001`.
- Workflow: `strategy-forward-replication-research@v005` at
  `workflows/strategy-forward-replication-research--v005`.
- Exact `revisits` target:
  `workflows/strategy-forward-replication-research--v004/work/studies/fxi-atr-band-mean-reversion-forward-replication--s004`.
- Workflow `RELEASE.json` SHA-256:
  `41801ebac5a7be68ea2f7ed240ca65edf9c43c94f1f3192a226971ec5bdf770b`.
- Workflow definition SHA-256:
  `ddc379ecf890694744d4e322543c6105646ba7e98bc7e91bdad8628ed2d8da82`.
- Canonical source Git HEAD at draft preparation:
  `aef248e1293ab1b3364ebdc3eeb636edad4107d3`.
- Composite policy set:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Proposed human research owner, preregistration approver, and new candidate-freeze approver:
  `ochowei@gmail.com`.
- Researcher identity: `codex-primary-researcher-fxi-mean-reversion`.

S004's candidate-freeze approval is lineage evidence only. It is not approval to preregister this
study, inspect 2010-2014 outcomes, or freeze a v005 retrospective candidate. This study remains
`draft` until the owner reviews the complete frozen summary and separately approves
preregistration. Outcome-relevant execution requires another later authorization after a new
candidate-freeze record.

The 2026-08-13 freshness audit reports the FXI AI context through 2025-12-31 and most cross-asset
lessons through 2025-12-31, older than six months. That warning cannot authorize refresh or newer
outcome inspection. Before preregistration, repeat the repository-wide freshness, contamination,
trial-history, source-identity, workflow, and policy checks; contrary evidence may only make the
boundary stricter.

### Released policy pins

| Family | Version | `RELEASE.json` SHA-256 |
| --- | --- | --- |
| `us-equity-market` | `v002` | `9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` |

No implicit `latest` workflow or policy is permitted. Every later Research Definition Snapshot,
qualification plan, manifest, observation, and screen must bind this exact v005 release and policy
set.

### Data roles, audit, and retrospective checkpoint

- Sole market-data dependency: Yahoo auto-adjusted daily OHLCV for `FXI`.
- Only completed XNYS-session observations may be used. Missing, duplicate, non-finite, stale, or
  session-invalid primary data fails closed.
- Proposed evaluation evidence role: `retrospective-confirmatory`.
- Frozen proposed classification: `provenance-unknown`. Repository records show legacy FXI source
  loading from 2010 but do not provide append-only evidence proving the 2010-2014 outcomes were
  unseen or that legacy selection history was complete. The classification may be tightened to
  `known-contaminated` before preregistration if contrary evidence is found; it may not be upgraded
  to `verified-clean` without qualifying append-only proof.
- The guarded qualification-plan registration must generate a current-time immutable
  `retrospective_selection_checkpoint`; it must never be represented as a Forward Selection Epoch.

| Role | Frozen completed sessions |
| --- | --- |
| Warmup only | All required 2009 XNYS observations plus fold-local leading warmup; no signal, fill, cooldown, or performance contribution |
| Retrospective confirmatory | Five consecutive annual folds: 2010, 2011, 2012, 2013, 2014 |
| Development context | S004's 2015-01-02 through 2025-12-31 evidence and all legacy FXI outcomes already viewed |
| Quarantined / out of scope | Every 2026 session, S004's 2027-2031 clean Historical folds, and all unassigned sessions |
| Shadow | Prohibited for this retrospective study |

For every retrospective fold, retain at least 21 prior completed sessions as warmup/dependency
observations, apply a one-session opening embargo, and purge the final 21 completed sessions from
signal generation. A trade belongs to its signal-date fold, enters no earlier than the next
completed session, and must enter and exit within that fold. Positions, signals, cooldown state,
P&L, and capital may not cross a fold or role boundary. Exact session inventories are generated and
frozen by the qualification plan before any retrospective outcome inspection.

### Fixed family and preregistration source work

`maximum_trials=6`. Every viewed outcome-relevant semantic definition consumes one slot; rerunning
the exact fingerprint adds an observation but not a trial. No seventh definition is allowed.

Six new permanent source entry points are prepared under
`src/trading/research_definitions/fxi-atr-band-mean-reversion-retrospective/`. They declare history
beginning on 2009-01-02 and research beginning on the first 2010 XNYS session, 2010-01-04. Apart
from family/result identity and those earlier data boundaries, their strategy, execution,
cooldown, cost, and policy semantics match the frozen S004 counterparts through provider-free
configuration and synthetic-candidate equivalence tests.

| Stable identity | Role | Frozen difference |
| --- | --- | --- |
| `fxi-atr-band-mean-reversion-retrospective/atr-band-candidate` | sole selected candidate | pullback, WR, ClosePos, ATR ratio in `(1.05, 1.35]` |
| `fxi-atr-band-mean-reversion-retrospective/pullback-wr-baseline` | distinct simple baseline | 5%-12% ten-session pullback and WR(10)<=-80 only; identical exits |
| `fxi-atr-band-mean-reversion-retrospective/atr-floor-1p10-robustness` | robustness only | candidate with strict ATR-ratio floor 1.10 |
| `fxi-atr-band-mean-reversion-retrospective/atr-ceiling-1p30-robustness` | robustness only | candidate with ATR-ratio ceiling 1.30 |
| `fxi-atr-band-mean-reversion-retrospective/hold-18-robustness` | robustness only | candidate with eighteen-session maximum holding |
| `fxi-atr-band-mean-reversion-retrospective/delay-one-session-robustness` | robustness only | candidate entry delayed one additional completed session |

Frozen source-byte inventory prepared for owner review:

| Identity / runtime / test | SHA-256 |
| --- | --- |
| `atr-band-candidate/definition.py` | `5b9470c4b74f7528fdcc336af55e883a3522f647ca0ae3c12f6c62d527b0fe3d` |
| `atr-ceiling-1p30-robustness/definition.py` | `0c56f410006a3429ef38081a1bc30631af1d0c46be59fac3ce8e0c5634bfe2c4` |
| `atr-floor-1p10-robustness/definition.py` | `1b19e102a35ea7b768d39c45e8cf5d3bc2162fc7ab71ab4ed525e547b90f4969` |
| `delay-one-session-robustness/definition.py` | `a6479f8eae8139a7fb7e58d1b48b2d84e7e7423e77f00391ad192df3fc1a6644` |
| `hold-18-robustness/definition.py` | `6f84334703079775aaaf7cb956374d7ad59babbcc05b3aeee4aad4f8a7892c1c` |
| `pullback-wr-baseline/definition.py` | `e50b9cdb4cca661acb964df10cd7e7c2b17a24eb38dc297b396704680e24e773` |
| shared `src/trading/research_definitions/fxi_mean_reversion.py` runtime | `120df54dde206dd16f6293bff7bf4f042b396d8970fd644458eadba677e2be7e` |
| `tests/test_workflow_native_fxi_mean_reversion_definition.py` | `0b0ce3e54bcca876f39dc61676f575e1c31cf3b8a251945ddf3c991ef55a64fb` |

The provider-free test suite verifies all six registry identities, the primary-only dependency,
exact configuration equivalence to the S004 counterparts after removing only the two date fields,
synthetic candidate/signal equality on an overlapping calendar, unchanged S004 research boundary,
and Research Definition Snapshot capture against the exact v005 policy set. Refresh, snapshot,
formal run, metric, ranking, qualification-plan registration, and 2010-2014 outcome inspection
remain prohibited.

The candidate selection is fixed from S004's already viewed Development context and deletion-only
follow-up rationale; it is not reranked using retrospective data. Before retrospective plan
registration, the v005 owner must create a new candidate-freeze record that pins all six source
identities, the complete family, distinct baseline, definitions, policy set, costs, gates, and this
study's preregistration. S004's freeze record cannot substitute for it.

### Frozen signal, execution, cooldown, and sleeve

- On completed session `t`, `High_N` is the maximum adjusted high over the inclusive last ten
  sessions. `Pullback=(adjusted_close-High_N)/High_N` must be between -12% and -5%, inclusive.
- Williams %R(10) uses inclusive rolling adjusted high/low and must be <= -80. A zero range is
  assigned -50 and cannot pass.
- `ClosePos=(adjusted_close-adjusted_low)/(adjusted_high-adjusted_low)` must be >= 0.40. A zero
  range is assigned 0.50.
- True range is the maximum of high-low, absolute high-prior-close, and absolute low-prior-close.
  Simple rolling `ATR(5)/ATR(20)` must be strictly greater than 1.05 and at most 1.35.
- Accepted signals use a ten-completed-session cooldown measured from the last accepted signal; a
  gap of ten or fewer sessions is suppressed and recorded.
- Entry is market at the next XNYS open. The target is a +5.5% Day limit, the stop is a -5.0% GTC
  stop-market, and both become active after entry on the entry session. Unresolved positions expire
  at the open after twenty completed holding sessions. Same-session target/stop ambiguity uses the
  pinned pessimistic ordering. Missing or non-finite prices never create inferred fills.
- Canonical isolated sleeve: normalized capital 1.0, fractional quantity, one position at a time,
  no leverage, pyramiding, cross-sleeve borrowing, rebalancing, or capital transfer.

Binding is measured before cooldown and occupation selection over valid core-baseline-eligible
decision sessions. ATR-floor suppression changes only the floor, ATR-ceiling suppression changes
only the ceiling, and complete-band suppression compares the full ATR band with the pullback/WR
baseline while retaining exact session/fold identities.

### Costs and deterministic challenges

- Gross definitions contain no embedded costs.
- Base costs: 5 bps entry slippage, 5 bps exit slippage, and 1 bp fee per side.
- Strict stress costs: 20 bps entry slippage, 20 bps exit slippage, and 2 bps fee per side.
- Exposure-matched random entries, twenty-session family-wise block bootstrap, and deterministic
  omission of 10% of otherwise executable entries use seed `20260813` and 1,000 replicas where
  replication applies.

## Method and stages

### 1. Draft and preregistration readiness

While status is `draft`, keep the six prepared provider-free source identities and synthetic tests
fixed, repeat repository/workflow/policy/freshness/contamination checks, verify that the full family
can be registered without legacy identity leakage, and show the complete frozen summary to the
owner.

Do not refresh data, create a market-data snapshot, register a retrospective qualification plan,
run any research identity, calculate or display 2010-2014 metrics, rank trials, or inspect a result.
Only explicit approval by stable human identity authorizes the separate guarded preregistration
command. After preregistration, `HYPOTHESIS.md` and `PLAN.md` are immutable.

### 2. Candidate freeze and retrospective plan registration

After preregistration, obtain separate explicit authorization to prepare and approve a new v005
candidate freeze. Verify all six source fingerprints and the complete family without market
outcomes. Then register exactly one `retrospective-confirmatory` qualification plan for 2010-2014,
with `provenance-unknown` (or stricter `known-contaminated` if the audit requires), complete new-
family trial history, the distinct baseline, current-time checkpoint, twenty-session holding,
one-session entry lag, 21 dependency sessions, one-session embargo, 20% stress drawdown limit,
seed 20260813, 1,000 random samples, 1,000 bootstrap repetitions, and 20-session blocks.

Stop if the production CLI cannot freeze the exact family/checkpoint/audit semantics without
manufacturing evidence or if any 2010-2014 outcome has already been exposed under the new family.

### 3. Retrospective execution and screen

Outcome-relevant execution requires a further explicit human authorization. Perform one full
refresh with an exact 2014-12-31 cutoff for the selected candidate; all other trials must reuse the
same eligible full-refresh generation without provider access. Before strategy-output inspection,
verify exact workflow/policy/source/data/plan/provenance bindings and immutable definition bytes.

Capture and run all six frozen trials because family-wise selection adjustment and the complete
challenge set require the full family. Supply one exact valid manifest per trial to the guarded
qualification screen. The screen must recompute annual and chained canonical-sleeve outcomes,
zero-signal folds, cash, baseline, exposure-matched random entries, complete-family block bootstrap,
both ATR perturbations, holding and delayed-entry perturbations, stress/worse-fill and missed-entry
challenges, concentration, binding counts, and annual China-equity regime evidence.

Do not tune, rerank, omit a trial, replace the baseline, or run a seventh definition. Record exact
plans, manifests, snapshot/definition IDs, results, complete commit SHA, checksums, commands, and
gate artifacts in `EVIDENCE.md`; do not write a conclusion.

### 4. Independent review and terminal boundary

After all planned evidence is complete, move the study only to `awaiting-review`. An independent
reviewer using `trading-evaluate-study` decides the study outcome. A passing screen may record only
`retrospectively-supported`; a failing complete screen records `retrospective-screen-failed`.

This study ends at that non-promotional disposition. It cannot register Shadow or alter S004.
S004's separate 2027-2031 clean Historical plan remains sealed and unchanged on v004.

## Metrics and outcome rules

All gates are conjunctive:

- five complete consecutive non-overlapping annual folds;
- at least 20 completed trades, at least three traded folds, and at least 60% positive traded folds;
- chained base return > 0 and profit factor > 1.1;
- chained stress return > 0, profit factor > 1.0, and maximum drawdown <= 20%;
- no fold contributes more than 50% of total trades or total positive profit;
- candidate base return >= 90% of baseline, Sharpe >= baseline plus 0.10, and stress drawdown no
  worse than baseline;
- ATR floor and ceiling each uniquely suppress at least two otherwise-candidate-eligible entries
  across at least two folds, and the complete band uniquely suppresses at least five core-baseline-
  eligible entries across at least three folds;
- candidate return exceeds cash and the 90th percentile exposure-matched random return;
- complete-family block-bootstrap selection confidence >= 90%;
- every perturbation, delayed entry, cost/fill, missed-entry, concentration, regime, source, role,
  and integrity challenge retains positive stress return, stress profit factor > 1.0, stress
  drawdown <= 20%, base return >= 90% of baseline, and Sharpe above baseline without reversing the
  claim.

Outcome interpretation under v005:

- `pass`: every required identity and retrospective gate is complete and passing; the only
  disposition is `retrospectively-supported` with no promotion authority.
- `fail`: any complete gate fails, either ATR-band side is non-binding, a robustness challenge
  reverses the claim, the complete six-trial family cannot be evaluated, or the trial budget is
  exhausted; disposition is `retrospective-screen-failed`.
- `insufficient-evidence`: not available for this closed completed-data checkpoint.
- `indeterminate`: any required identity, classification, checkpoint, trial history, source byte,
  data, policy pin, provenance, replay, role isolation, approval, or evidence is missing, stale,
  corrupt, conflicting, or unverifiable. Advancement stops; no partial evidence supports the claim.

## Deviations and stopping rules

After preregistration, do not change the claim, folds, classification except to a stricter audit
class, data roles, family, source identities, trial budget, signal formula, cooldown, exits,
baseline, costs, execution timing, warmup, purge, embargo, seeds, binding definitions, thresholds,
challenges, or outcome rules. Do not add ASHR/CNY/VIX/EEM/trend/gap/BB-width/oscillator filters,
import a legacy identity, let a robustness trial become the candidate, or use 2010-2014 outcomes to
repair the definition.

Any outcome-relevant design change requires cancellation and a new CLI-allocated study with exact
lineage. Once viewed, 2010-2014 becomes Development context for any changed lineage and cannot be
reused as confirmation.

Pause or stop on incomplete/stale data, source/release drift, invalid manifests, trial-family
incompleteness, qualification-plan incompatibility, role leakage, provenance/replay failure,
missing exact bytes, or unauthorized outcome exposure. Terminate on any complete retrospective
gate failure, unrecoverable integrity problem, semantic definition change, exhausted trial budget,
or explicit owner stop. This draft authorizes no outcome-relevant run, broker access, order, Shadow,
activation, or live-trading action.
