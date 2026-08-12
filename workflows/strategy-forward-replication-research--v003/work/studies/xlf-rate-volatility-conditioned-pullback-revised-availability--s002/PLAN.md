# Plan: XLF Rate-Volatility-Conditioned Pullback Revised Availability Research

## Inputs and frozen identities

### Governance and authority

- Workflow: `strategy-forward-replication-research@v003`.
- Workflow release SHA-256:
  `9c5a554751a70d6c286fa0ca938ee171cc5da81d2e683d29b11ba06579aad183`.
- Workflow definition SHA-256:
  `11cebc16588c2feae2637128b4b18a015d0de65507ee47096ae0a3e8aec0370f`.
- Composite policy set:
  `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.
- Human research owner and preregistration/candidate-freeze approver: `ochowei@gmail.com`.
- Researcher/operator: `codex-primary-researcher-xlf-s002`.
- Exact revisit: `workflows/strategy-forward-replication-research--v003/work/studies/xlf-rate-volatility-conditioned-pullback--s001`.

### Market data and roles

- Primary: Yahoo auto-adjusted daily OHLCV for `XLF`, XNYS-complete coverage, required from
  1998-12-22.
- Auxiliary for gated candidates: Yahoo auto-adjusted daily OHLCV for `^MOVE`, provider-observation
  coverage, required from 1998-12-22. Publication time is unknown; every decision uses only the
  most recent observation after one XNYS-session publication lag, with maximum lag three sessions.
- Warmup only: 1998-12-22 through 1999-12-31. Development: 2000-01-03 through 2020-12-31.
  Historical: five annual folds, 2021 through 2025. Pre-registration 2026 data is quarantined;
  Shadow is prospective only after a passing Historical screen and current-time registration.
- Each Development/Historical segment has 21 initial warmup-only primary sessions and 11 final
  purged signal sessions. Positions cannot cross data roles or annual folds.

### Candidate inventory and trial accounting

`maximum_trials=6`; every viewed outcome-relevant semantic definition consumes one slot, while a
repeat of the exact fingerprint adds only an observation.

| Stable identity | Role | Frozen difference |
| --- | --- | --- |
| `xlf-rate-volatility-conditioned-pullback-revised-availability/move-direction-cap-3` | candidate | MOVE 3-session change <= +3 |
| `xlf-rate-volatility-conditioned-pullback-revised-availability/move-direction-cap-5` | candidate | MOVE 3-session change <= +5 |
| `xlf-rate-volatility-conditioned-pullback-revised-availability/move-direction-cap-7` | candidate | MOVE 3-session change <= +7 |
| `xlf-rate-volatility-conditioned-pullback-revised-availability/ungated-pullback-baseline` | simple baseline | no MOVE gate |
| `xlf-rate-volatility-conditioned-pullback-revised-availability/selected-cap-minus-one-robustness` | robustness only | selected cap minus one point |
| `xlf-rate-volatility-conditioned-pullback-revised-availability/selected-entry-lag-two-robustness` | robustness only | selected cap, entry at t+2 open |

The last two identities are materialized only after Development selection. They cannot win
selection, and no seventh semantic trial is allowed. These S002 identities are distinct from and
do not mutate S001's permanent source identities.

### Frozen signal and execution

- Signal at completed session `t`: XLF close <= its 20-session mean minus 2.0 sample standard
  deviations and ten-session adjusted-close return <= -4%.
- Gated candidates additionally require the backward-as-of aligned MOVE three-decision-session
  close change <= the candidate cap.
- Entry is next XNYS open (`t+1`), exit is the open ten completed sessions after entry; the delayed
  robustness enters at `t+2`. Missing/non-finite opens are integrity failures.
- Canonical isolated sleeve: normalized capital 1.0, fractional quantity, one position, no leverage,
  pyramiding, rebalancing, or capital transfer. Released canonical base/stress execution costs are
  applied only by the canonical sleeve evaluator.

## Method and stages

### 1. Preregistration

Validate the workflow/policy pins, all four source identities, the corrected data declarations,
trial inventory, roles, gates, and explicit human approval. Generate `PREREGISTRATION.json` before
any S002 refresh, snapshot, formal run, metric calculation, result inspection, or ranking.

### 2. Development and candidate selection

After explicit advancement, snapshot cap-3 first with the standard command, causing the one
authoritative full refresh of XLF and MOVE through 2020-12-31. Snapshot cap-5 and cap-7 with
`--reuse-full-refresh`; snapshot the baseline with the same reuse mode. Reuse must perform no
provider access and remains subject to full-refresh eligibility, coverage, and cutoff validation.

Before any run, verify that all four manifests reference one identical XLF data-blob digest and all
three gated manifests reference one identical MOVE digest. Any difference stops the study without
execution or partial ranking. Each manifest must bind its own immutable S002 definition snapshot,
the v003 release/workflow hashes, exact policy set, full Git HEAD, canonical argv, and exact
orchestration bytes.

A candidate is eligible only with at least 30 completed base-net trades across ten traded calendar
years, base return > 0, base profit factor > 1.1, stress return > 0, stress profit factor > 1.0,
stress maximum drawdown <= 15%, no unresolved integrity difference, and base-net daily-equity
Sharpe at least 0.25 above the ungated baseline. Rank all eligible candidates by Sharpe descending;
ties use cap-3, cap-5, cap-7 order. No eligible candidate is a Development `fail`.

Persist the complete candidate set, identities, gates, ranking, and rationale. Materialize the two
deterministic robustness definitions only for the selected cap. Human owner approval is required
before candidate freeze or Historical access.

### 3. Historical Evaluation and robustness

Evaluate only the frozen candidate, baseline, and two robustness definitions on annual 2021-2025
folds. Required challenges: cash; baseline; 1,000 exposure-matched random entries; family-wise
20-session block bootstrap across the three candidates; cap-minus-one; delayed entry; stress/worse
fills; deterministic 10% entry omission; and annual regimes. Both randomized procedures use seed
`20260812`. Challenges can falsify but cannot replace the candidate.

### 4. Shadow and later stages

Only persisted passing Historical evidence permits current-time prospective Shadow registration.
Shadow requires at least 252 completed sessions and 12 completed simulated fills. It remains
non-actionable; activation and monitoring require all separate v003 controls.

## Metrics and outcome rules

Historical gates are conjunctive: five complete folds; at least 20 completed trades; at least three
traded folds; at least 60% positive traded folds; chained base return > 0 and profit factor > 1.1;
chained stress return > 0 and profit factor > 1.0; stress drawdown <= 15%; no fold over 50% of total
trades or positive profit; candidate Sharpe advantage >= 0.25 over baseline; return above cash,
baseline, and the 90th percentile random-entry return; family-wise confidence >= 90%; and no
required robustness challenge with non-positive stress return, stress profit factor <= 1.0,
drawdown > 15%, integrity failure, or reversed MOVE-direction evidence.

- `pass`: all complete Historical identities and gates pass; grants only `shadow-eligible`.
- `fail`: a complete Development/Historical gate fails or the six-trial budget is exhausted.
- `insufficient-evidence`: only an open prospective Shadow checkpoint allowed by v003.
- `indeterminate`: identity, data, source, policy, provenance, replay, or gate evidence is missing,
  stale, corrupt, conflicting, or unverifiable.

## Deviations and stopping rules

After preregistration, do not change data roles, candidate inventory, trial budget, formulas,
thresholds, auxiliary availability, snapshot-reuse procedure, common-blob equality requirement,
selection rule, baseline, costs, execution, purge/embargo, gates, seeds, or outcomes. Any such
change requires cancellation and a new revisiting study.

Pause on stale/incomplete data, unequal common-series blobs, digest drift, missing source bytes,
invalid manifests, parity/provenance mismatch, or partial candidate availability. Terminate when no
Development candidate is eligible, trial budget is exhausted, a Historical/Shadow gate fails, a
frozen definition changes materially, evidence is unrecoverable, or the owner stops the study.
Never repair an unfavorable result, hide a trial, loosen a cap/gate, or use Historical/Shadow
outcomes to redesign or rerank candidates.
