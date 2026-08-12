# Plan: ACWI Turn-of-Month Integrity Replication

## Inputs and frozen identities

### Governance and provenance

- Workflow: `strategy-forward-replication-research@v002`
- Workflow release SHA-256:
  `34ba7bb1518df9e46f4f1d89330b6c1e005225c007bfad43440a3d9a75e90299`
- Workflow definition SHA-256:
  `4dfa7df8244744aab3219c1a0784aee8af9ca559c059e5cb659aa6088b7789be`
- Study: `strategy-forward-replication-research@v002/S003`
- Human research owner, preregistration approver, candidate-freeze approver:
  `ochowei@gmail.com`
- Revisits:
  `workflows/strategy-forward-replication-research--v002/work/studies/acwi-turn-of-month-replication-revised-availability--s002`
- S002 terminal outcome: `indeterminate`, reviewed by `codex-independent-reviewer-s002`; its
  Development outcomes are known provenance and never Historical evidence.

The execution agent is identified at transition time and cannot review or complete S003. The
independent reviewer must not participate in topic selection, plan/source authoring, execution,
evidence production, or candidate freeze.

### Exact policy set

Composite identity:
`4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.

| Family | Release | `RELEASE.json` SHA-256 | `policy.yaml` SHA-256 |
| --- | --- | --- | --- |
| `us-equity-market` | `v001` | `7df1e266aa72ccfaca3efa3e490ad6234f300bb0bfc4e31b3dd3c85ab93de542` | `c2944014942674483d326aa45b34adcc9e8629bcfb53a315b2d029a84a547d10` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` | `beb47a951fbae842ebea79353f6c31dcf784a74537d48d1e8e8c696d0618ec28` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` | `fd7cbb7bfd77887b557c2c9075124adb6a1b77e6789bd6cf91971e44646be5f8` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` | `0c1f786cfe686ec9633c6d0ff70d2d1fab9053fd5040c4f0487c6d047aabb9dc` |

Every snapshot and run re-resolves these releases. Missing, duplicate, retired, implicit-latest, or
digest-drifted policy evidence is `indeterminate`.

### Data roles

- Primary series: Yahoo auto-adjusted ACWI daily OHLCV, XNYS sessions, no auxiliary/private data.
- `2008-03-28` through `2008-12-31`: availability/warmup only.
- `2009-01-01` through `2020-12-31`: Development integrity-replication evidence. S002 outcomes for
  this interval are known; therefore it is not validation evidence and cannot justify threshold or
  inventory changes.
- `2021-01-01` through `2025-12-31`: five complete consecutive non-overlapping Historical folds.
  S001 and S002 did not inspect them. They remain sealed until candidate freeze and separate human
  advancement approval.
- `2026-01-01` through preregistration: quarantine/unused.
- Shadow is outside this Historical-only study and cannot be backfilled.

### Trial inventory

`maximum_trials=6`. The S003 round starts with four source identities. Every outcome-relevant
semantic fingerprint first observed in S003 counts once; a failed or abandoned fingerprint remains
visible. Exact reruns append observations without increasing the count.

| Stable identity | Role | Frozen semantics |
| --- | --- | --- |
| `acwi-turn-of-month/enter-minus-two-hold-five` | candidate | enter `M-2` open, hold five complete sessions, next-open expiry |
| `acwi-turn-of-month/enter-minus-one-hold-five` | candidate | enter `M-1` open, otherwise identical |
| `acwi-turn-of-month/enter-month-end-hold-five` | candidate | enter `M0` open, otherwise identical |
| `acwi-turn-of-month/enter-session-ten-hold-five` | baseline | enter tenth monthly XNYS session, otherwise identical |
| `acwi-turn-of-month/selected-hold-four` | robustness only | selected offset, four-session holding dependency |
| `acwi-turn-of-month/selected-hold-six` | robustness only | selected offset, six-session holding dependency |

Only the first three may be selected. Hold-four/six sources are materialized only after candidate
freeze and before any Historical inspection. Current source contains the pre-outcome partial-month
coverage repair discovered in S002; no further semantic repair is allowed after preregistration.

### Execution and immutable observation protocol

- Signal on the complete session immediately before the selected entry; entry at next selected
  session open. Five complete holding sessions followed by next-open expiry.
- Maximum holding dependency 6, lag 1, purge 7, embargo 1. Annual folds admit only positions whose
  entry and exit remain within the fold.
- Isolated sleeve, initial capital `1.0`, one position maximum, no pyramiding, borrowing,
  cross-sleeve transfer, target, or stop.
- Base per side: 5 bps slippage plus 1 bp fee. Stress per side: 20 bps slippage plus 2 bp fee.
- Missing next session is unfilled. Pinned adverse intrabar semantics remain in force.

Every formal result must embed `metadata.observation_provenance` generated before strategy output
inspection. It must contain:

1. canonical application argv with exact research identity, workflow path, manifest path, and
   offline mode;
2. workflow family/version/path, v002 release SHA-256, workflow SHA-256, and composite policy-set
   identity;
3. complete Git HEAD;
4. exact UTF-8 bytes plus SHA-256 for `src/trading/cli.py`,
   `src/trading/research_definitions/execution.py`, `src/trading/research_data/runs.py`, and
   `src/trading/research_data/result_schema.py`.

Evidence must independently recompute those hashes, verify that the embedded canonical argv agrees
with the recorded command, verify snapshot/definition blobs provider-free, and record manifest and
result SHA-256. Operator prose cannot replace a missing embedded field. Snapshot and refresh
commands, stdout/stderr disposition, timestamps, failure identities, complete Git HEAD, and dirty
status/diff are recorded exactly in `EVIDENCE.md` before any metric comparison.

## Method and stages

### 1. Preregistration

Show this complete frozen plan and hypothesis to `ochowei@gmail.com`. Preregister only after an
explicit approval naming S003. A general instruction to proceed is not preregistration approval.
After preregistration, obtain separate authorization before transition, refresh, snapshot, run, or
outcome inspection.

### 2. Development integrity replication

After authorization, capture new immutable snapshots capped at `2020-12-31` for all three
candidates and the baseline. Run them offline with the exact v002 path. Do not inspect metrics until
all four observations and provenance payloads validate. Missing evidence stops selection; partial
ranking is forbidden.

Apply the frozen gates and selection rule. If no candidate qualifies, stop without inspecting
2021+. If exactly one candidate is selected, materialize hold-four/six sources, record all six
fingerprints, and obtain explicit candidate-freeze/Historical-stage approval from
`ochowei@gmail.com`.

### 3. Historical Evaluation

Before first Historical outcome, register the full six-trial family with annual folds 2021-2025,
maximum holding 6, lag 1, purge 7, embargo 1, seed `20260812`, 1,000 exposure-matched random
samples, and 1,000 family-wise block-bootstrap repetitions using 20-session blocks. Capture
manifests only through `2025-12-31` and recompute with maintained qualification code.

Challenges are cash, tenth-session baseline, random entries, family-wise adjustment, non-selected
offsets, hold 4/6, one-session extra delay, stress costs, deterministic 10% missed entries keyed by
SHA-256 of `plan-id:trial-id:signal-date`, and per-fold regime/zero-signal reporting. Challenges may
falsify but never replace the frozen candidate.

### 4. Review boundary

After the reachable stage reaches a recorded terminal result, update only `EVIDENCE.md`, transition
to `awaiting-review`, and stop. An independent `trading-evaluate-study` reviewer alone writes
`CONCLUSION.md` and completes the study.

## Metrics and outcome rules

### Development gates and selection

Each candidate requires, on 2009-2020 only:

- at least 20 completed trades and at least one in every Development year;
- base compounded return > 0 and profit factor > 1.10;
- stress compounded return > 0 and profit factor > 1.00;
- stress maximum drawdown >= `-15%`;
- base-net daily-equity Sharpe strictly greater than baseline Sharpe plus `0.15`;
- no calendar year contributes more than 50% of trades or positive profit under either `base_net`
  or `stress_net`.

For each cost scenario independently, annual positive-profit concentration is the largest positive
calendar-year net realized P&L divided by the sum of positive calendar-year net realized P&L. Trade
concentration is the largest annual completed-trade count divided by all completed trades. A zero
positive-profit denominator fails the positive return/profit-factor gates and cannot pass by making
concentration undefined.

Every identity, provenance field, parity classification, artifact, and checksum must validate.
Select the eligible candidate with highest canonical base-net daily-equity Sharpe; exact ties use
lexicographic stable identity. No eligible candidate or exhausted budget is terminal `fail`.

### Historical and robustness gates

- five complete annual folds, at least 20 trades, at least 3 traded folds, and at least 60% positive
  traded folds;
- base return > 0/PF > 1.10; stress return > 0/PF > 1.00; stress MDD >= `-15%`;
- for both base-net and stress-net, no fold exceeds 50% of trades or positive profit, using the same
  concentration definition as Development;
- compounded return strictly exceeds cash, baseline, and random-entry 90th percentile;
- family-wise block-bootstrap adjusted confidence >= 90% across all six trials;
- non-selected offsets and hold 4/6 each retain positive base/stress return and compliant stress
  MDD;
- delayed-entry and deterministic missed-entry challenges retain positive stress return and
  compliant stress MDD;
- all folds, exclusions, zero-signal folds, unfilled entries, regimes, identities, commands,
  embedded orchestration sources, and checksums remain visible and valid.

`pass` requires every reachable frozen gate and means only `shadow-eligible`. `fail` follows any
complete failed gate or exhausted budget. `insufficient-evidence` is unavailable for these fixed
stages. `indeterminate` follows an unrecoverable approval, identity, command, workflow binding,
source capture, checksum, commit, data, family, or reproducibility defect.

## Deviations and stopping rules

After preregistration do not change ticker, dates, candidates, baseline, budget, data roles, costs,
concentration scenario, formula, thresholds, selection, commands, provenance schema,
randomization, stopping, or outcomes. Never tune from known S002/S003 Development results, inspect
Historical early, reuse Historical after failure, hide trials, partial-rank, contact a broker,
submit orders, claim live authorization, or store private data under `workflows/`.

Pause on provider/data incompleteness, digest drift, uncaptured source, corrupt provenance,
implementation mismatch, family drift, missing approval, or governance defect. Repair only the
same frozen evidence when its immutable identity already exists; newly produced evidence belongs
to this preregistered S003 execution and cannot be backdated. A research-design change requires
cancellation and a new revisiting study. A released-workflow defect requires workflow version
governance and is never patched in place.

Terminate on Development/Historical `fail`, unrecoverable `indeterminate`, exhausted budget,
post-freeze semantic change, or human-owner stop. No robustness source, Historical snapshot, or
2021+ outcome is permitted after a Development stop.
