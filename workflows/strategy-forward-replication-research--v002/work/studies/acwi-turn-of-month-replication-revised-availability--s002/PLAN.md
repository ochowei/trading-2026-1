# Plan: ACWI Turn-of-Month Replication — Corrected Availability

## Inputs and frozen identities

### Governance

- Workflow: `strategy-forward-replication-research@v002`
- Workflow path: `workflows/strategy-forward-replication-research--v002`
- Workflow `RELEASE.json` SHA-256:
  `34ba7bb1518df9e46f4f1d89330b6c1e005225c007bfad43440a3d9a75e90299`
- Workflow definition SHA-256:
  `4dfa7df8244744aab3219c1a0784aee8af9ca559c059e5cb659aa6088b7789be`
- Study: `strategy-forward-replication-research@v002/S002`
- Revisits:
  `workflows/strategy-forward-replication-research--v002/work/studies/acwi-turn-of-month-replication--s001`
- Human research owner, preregistration approver, and candidate-freeze approver:
  `ochowei@gmail.com`
- Creator: `ochowei@gmail.com`
- Execution agent is identified at execution time and cannot review or complete the study. The
  independent reviewer must not participate in topic selection, plan/source authoring, execution,
  evidence production, or candidate freeze.

S001 was cancelled because its required start `2008-03-26` preceded the first provider row
`2008-03-28`. Its four snapshots failed bundle verification before strategy execution and produced
no metrics, observations, ranking, or Historical inspection. S002 changes only the
availability/warmup start to `2008-03-28`; hypothesis, performance data roles, candidate inventory,
selection, costs, gates, challenges, and stopping rules remain unchanged.

### Exact policy set

Composite policy-set identity:
`4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.

| Family | Release | `RELEASE.json` SHA-256 | `policy.yaml` SHA-256 |
| --- | --- | --- | --- |
| `us-equity-market` | `v001` | `7df1e266aa72ccfaca3efa3e490ad6234f300bb0bfc4e31b3dd3c85ab93de542` | `c2944014942674483d326aa45b34adcc9e8629bcfb53a315b2d029a84a547d10` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` | `beb47a951fbae842ebea79353f6c31dcf784a74537d48d1e8e8c696d0618ec28` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` | `fd7cbb7bfd77887b557c2c9075124adb6a1b77e6789bd6cf91971e44646be5f8` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` | `0c1f786cfe686ec9633c6d0ff70d2d1fab9053fd5040c4f0487c6d047aabb9dc` |

Every formal run re-resolves these exact releases. Implicit latest, digest drift, missing or
duplicate family, or workflow/policy resolution failure is `indeterminate`.

### Market data, decision semantics, and data roles

- Primary series: Yahoo auto-adjusted daily OHLCV for `ACWI`, XNYS calendar, no auxiliary or private
  data.
- Information cutoff: completed daily sessions only. Let `M0` be each month's final scheduled XNYS
  session. Candidate entry sessions are `M-2`, `M-1`, or `M0`; the signal/decision session is the
  immediately preceding completed XNYS session and entry is at the selected session's open.
- 2008-03-28 through 2008-12-31: availability/warmup only; no performance contribution.
- 2009-01-01 through 2020-12-31: Development selection evidence.
- 2021-01-01 through 2025-12-31: five complete consecutive non-overlapping annual Historical
  Evaluation folds. No Historical outcome may affect candidate selection or thresholds.
- 2026-01-01 through preregistration: quarantine/unused; it cannot affect selection, thresholds,
  interpretation, Historical result, or Shadow.
- Shadow is outside this Historical-only study. It may be registered at current UTC only after a
  persisted passing Historical Screen; no earlier session may be backfilled.
- Formal observations require full refresh at the frozen cutoff, immutable market-data and Research
  Definition Snapshots, v002 orchestration-source identity, complete commit SHA, checksums, and
  provider-free replay evidence.

Repository search found no legacy ACWI experiment, workflow-native ACWI observation, retained ACWI
result, or prior ACWI selection history. S001 created only coverage-invalid snapshots and no
outcome. Public anomaly knowledge is design provenance, controlled by the complete family,
baseline, random benchmark, and family-wise adjustment. Stale cross-asset lessons are general safety
context only and cannot supply ACWI evidence or thresholds.

### Trial budget and inventory

`maximum_trials=6`. Each outcome-relevant semantic fingerprint counts once; exact reruns add
observations, not trials. Failed, invalid, removed, unfilled, or abandoned attempts remain visible.

| Stable source identity | Role | Frozen semantics |
| --- | --- | --- |
| `acwi-turn-of-month/enter-minus-two-hold-five` | selection candidate | entry at `M-2` open; hold five complete sessions; next-open expiry |
| `acwi-turn-of-month/enter-minus-one-hold-five` | selection candidate | entry at `M-1` open; otherwise identical |
| `acwi-turn-of-month/enter-month-end-hold-five` | selection candidate | entry at `M0` open; otherwise identical |
| `acwi-turn-of-month/enter-session-ten-hold-five` | distinct baseline | entry at tenth monthly XNYS session; otherwise identical |
| `acwi-turn-of-month/selected-hold-four` | robustness-only | selected offset; four complete holding sessions |
| `acwi-turn-of-month/selected-hold-six` | robustness-only | selected offset; six complete holding sessions |

Only the first three can win. Baseline and robustness definitions cannot be selected. Robustness
sources are materialized after candidate freeze and before Historical inspection. Non-selected
offsets remain visible as timing perturbations and cannot replace the selected candidate.

### Execution dependencies and costs

- One-session decision/entry lag; next-open market entry.
- Five complete holding sessions followed by next-open expiry; four/six only for frozen challenges.
- Maximum holding dependency 6, dependency purge 7, opening embargo 1.
- Annual folds admit only signals whose entry and exit remain in-fold; no carry-in or synthetic
  force-close. Excluded cross-boundary signals are reported.
- One isolated sleeve, initial capital `1.0`, at most one position, no pyramiding, borrowing,
  cross-sleeve transfers, or evaluation-period rebalancing.
- Base per side: 5 bps slippage + 1 bp fee; 12 bps round trip.
- Stress per side: 20 bps slippage + 2 bps fee; 44 bps round trip.
- Missing next session is unfilled. No target/stop is used; pinned adverse intrabar semantics remain
  part of the policy set.

## Method and stages

### 1. Preregistration

After `ochowei@gmail.com` approves this complete corrected frozen summary, preregister through the
workflow CLI. Do not transition, refresh, snapshot, execute, or inspect outcomes before separate
post-preregistration authorization.

### 2. Source and Development

Formal source belongs only under `src/trading/research_definitions/acwi-turn-of-month/`, never the
legacy tree. Capture immutable Development snapshots capped at `2020-12-31` and run all three
candidates plus baseline offline. All four valid observations must exist before eligibility or
ranking. If no candidate qualifies, stop with Development `fail` without inspecting 2021+ outcome.

If selected, materialize hold-four/six definitions, record all six fingerprints, and obtain explicit
candidate-freeze/Historical-stage approval from `ochowei@gmail.com` before Historical inspection.

### 3. Historical Evaluation and robustness

Before first Historical outcome, register the complete family and plan with annual folds 2021-2025,
maximum holding 6, lag 1, purge 7, embargo 1, seed `20260812`, 1,000 exposure-matched random samples,
and 1,000 family-wise block-bootstrap repetitions using 20-session blocks.

Capture manifests through `2025-12-31` and recompute with maintained qualification code. Challenges:
cash, mid-month baseline, random entries, family-wise adjustment, non-selected offsets, hold 4/6,
one-session extra delay, stress costs, deterministic 10% missed entries keyed by SHA-256 of
`plan-id:trial-id:signal-date`, and per-fold regime/zero-signal reporting. Challenges cannot replace
the candidate and partial ranking is prohibited.

### 4. Independent review and terminal scope

After complete evidence, update only `EVIDENCE.md`, transition to `awaiting-review`, and stop.
An independent `trading-evaluate-study` reviewer writes `CONCLUSION.md` and completes the study.
Historical `pass` means only `shadow-eligible`; no Shadow registration, activation, broker access,
orders, private ledger data, or live authorization occurs in this study.

## Metrics and outcome rules

### Development eligibility and selection

Using 2009-2020 only, each candidate requires:

- at least 20 completed trades and at least one in every Development year;
- base return > 0 and profit factor > 1.10;
- stress return > 0 and profit factor > 1.00;
- stress maximum drawdown >= `-15%`;
- no year contributes >50% of trades or positive profit;
- base-net daily-equity Sharpe strictly exceeds baseline by at least `0.15`;
- exact data/definition/policy/workflow/orchestration/result identities validate without
  unclassified parity difference.

Select one eligible candidate by descending canonical base-net daily-equity Sharpe; exact ties use
lexicographic stable identity. Invalid/stale required evidence stops selection; no partial ranking.
No eligible candidate or trial-budget exhaustion is terminal `fail`.

### Historical and robustness gates

- five complete annual folds, at least 20 trades, at least 3 traded folds, at least 60% positive
  traded folds;
- base return >0/PF >1.10; stress return >0/PF >1.00; stress MDD >=`-15%`;
- no fold >50% of total trades or positive profit;
- compounded return strictly exceeds cash, baseline, and random-entry 90th percentile;
- family-wise block-bootstrap adjusted confidence >=90% across all six trials;
- both non-selected offset and hold 4/6 challenges retain positive base and stress compounded
  return and stress MDD >=`-15%`;
- one-session delayed-entry and deterministic missed-entry challenges retain positive stress
  compounded return and stress MDD >=`-15%`;
- all folds, exclusions, zero-signal folds, unfilled entries, regimes, identities, and checksums are
  visible and valid.

Outcomes: `pass` only if all gates pass and means `shadow-eligible`; `fail` for any complete failed
gate or exhausted budget; `insufficient-evidence` is unavailable for fixed Development/Historical;
`indeterminate` for unrecoverable approval, identity, artifact, source-capture, checksum, commit,
data, family, or reproducibility defects.

## Deviations and stopping rules

After preregistration never edit `HYPOTHESIS.md` or `PLAN.md`, or change ticker, dates, offsets,
candidates, budget, selection, baseline, costs, dependencies, thresholds, randomization, stopping,
or outcomes. Do not tune from Development failure, inspect Historical early, reuse Historical after
failure, hide trials, weaken gates, partial-rank, contact a broker, submit orders, claim live
authorization, or store private data under `workflows/`.

Pause on provider/data incompleteness, digest drift, uncaptured dirty source, corruption, family
drift, missing human approval, or governance defect. Repair only identical frozen evidence. Any
meaning change requires cancellation and a new exact `revisits` study; released defects require
version governance and are never patched in place.

Terminate on Development/Historical `fail`, unrecoverable `indeterminate`, exhausted budget,
post-freeze definition change, or human-owner stop. Every observation records exact workflow/policy
releases, policy-set identity, immutable snapshots, orchestration identity, complete Git HEAD and
dirty status/diff, command, result identity/path, and SHA-256; study evidence stores references only.
