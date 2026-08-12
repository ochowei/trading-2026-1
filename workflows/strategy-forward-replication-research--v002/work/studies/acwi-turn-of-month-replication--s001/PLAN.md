# Plan: ACWI Turn-of-Month Replication

## Inputs and frozen identities

### Governance

- Workflow: `strategy-forward-replication-research@v002`
- Workflow path: `workflows/strategy-forward-replication-research--v002`
- Workflow `RELEASE.json` SHA-256:
  `34ba7bb1518df9e46f4f1d89330b6c1e005225c007bfad43440a3d9a75e90299`
- Workflow definition SHA-256:
  `4dfa7df8244744aab3219c1a0784aee8af9ca559c059e5cb659aa6088b7789be`
- Study: `strategy-forward-replication-research@v002/S001`
- Human research owner, preregistration approver, and candidate-freeze approver:
  `ochowei@gmail.com`
- Creator: `ochowei@gmail.com`
- Execution agent identity is recorded when execution begins and cannot review or complete the
  study. The independent reviewer must not have participated in topic selection, plan/source
  authoring, execution, evidence production, or candidate freeze.
- This study does not revisit S001 under v001. The prior SCHD down-streak pilot is governance
  provenance only and supplies no ACWI outcome evidence.

### Exact policy set

Composite policy-set identity:
`4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.

| Family | Release | `RELEASE.json` SHA-256 | `policy.yaml` SHA-256 |
| --- | --- | --- | --- |
| `us-equity-market` | `v001` | `7df1e266aa72ccfaca3efa3e490ad6234f300bb0bfc4e31b3dd3c85ab93de542` | `c2944014942674483d326aa45b34adcc9e8629bcfb53a315b2d029a84a547d10` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` | `beb47a951fbae842ebea79353f6c31dcf784a74537d48d1e8e8c696d0618ec28` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` | `fd7cbb7bfd77887b557c2c9075124adb6a1b77e6789bd6cf91971e44646be5f8` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` | `0c1f786cfe686ec9633c6d0ff70d2d1fab9053fd5040c4f0487c6d047aabb9dc` |

Definition capture and every formal run must re-resolve these exact releases and composite
identity. Implicit latest, digest drift, missing family, duplicate family, or policy/workflow
resolution failure is `indeterminate` and stops work.

### Market data, decision semantics, and data roles

- Primary series: Yahoo auto-adjusted daily OHLCV for `ACWI`, using the XNYS calendar; no auxiliary
  market-data series and no private data.
- Information cutoff: only completed daily sessions under `us-equity-market@v001`. The monthly
  XNYS schedule is calendar information, not future price information.
- For each month, let `M0` be its final scheduled XNYS session. Entry-offset identities select
  `M-2`, `M-1`, or `M0` as the entry session. The signal/decision session is the immediately
  preceding completed XNYS session; entry occurs at the selected session's open.
- 2008-03-26 through 2008-12-31: availability/warmup only; no performance contribution.
- 2009-01-01 through 2020-12-31: Development selection evidence.
- 2021-01-01 through 2025-12-31: five complete, consecutive, non-overlapping annual Historical
  Evaluation folds. No ACWI outcome from these sessions may be inspected before preregistration;
  no Historical outcome may affect candidate selection or thresholds.
- 2026-01-01 through preregistration: quarantine/unused. It cannot change the candidate, selection,
  thresholds, interpretation, or Historical result and is not counted as Shadow.
- Shadow is outside this Historical-only study. A later action may register prospective Shadow at
  current UTC only after a persisted passing Historical Screen; no pre-registration session may
  be backfilled.
- Each formal observation requires a full refresh capped at its frozen decision session, immutable
  market-data and Research Definition Snapshots, exact orchestration-source identity required by
  v002, complete Git commit SHA, checksums, and provider-free replay evidence.

Repository search found no legacy `ACWI` experiment, workflow-native ACWI family, retained ACWI
result, or prior ACWI selection history. Before preregistration no ACWI refresh, execution, or
outcome inspection was performed. Public knowledge of a turn-of-month anomaly is design provenance,
not evidence; publication and selection bias are controlled by the complete frozen family,
distinct baseline, random benchmark, and family-wise adjustment. Cross-asset lessons with
`data_through: 2025-12-31` are stale by the repository six-month rule and may supply only general
safety context, never ACWI outcome evidence or threshold selection.

### Trial budget and inventory

`maximum_trials=6`. Every outcome-relevant semantic fingerprint counts once. Re-running the same
fingerprint adds an observation, not a trial. Failed, removed, invalid, unfilled, or abandoned
observations remain in the append-only family history.

| Stable source identity | Role | Frozen semantics |
| --- | --- | --- |
| `acwi-turn-of-month/enter-minus-two-hold-five` | selection candidate | entry at `M-2` open; hold five complete sessions; next-open expiry |
| `acwi-turn-of-month/enter-minus-one-hold-five` | selection candidate | entry at `M-1` open; otherwise identical |
| `acwi-turn-of-month/enter-month-end-hold-five` | selection candidate | entry at `M0` open; otherwise identical |
| `acwi-turn-of-month/enter-session-ten-hold-five` | distinct baseline | entry at the tenth XNYS session of each month; otherwise identical |
| `acwi-turn-of-month/selected-hold-four` | robustness-only | selected entry offset; four complete holding sessions |
| `acwi-turn-of-month/selected-hold-six` | robustness-only | selected entry offset; six complete holding sessions |

Only the first three definitions can win selection. The baseline and robustness trials cannot be
selected. The robustness sources are materialized deterministically after candidate freeze and
before Historical inspection. The two non-selected entry offsets remain visible and serve as the
predeclared entry-timing perturbations; challenges can support or falsify but never replace the
selected candidate.

### Execution dependencies and costs

- Entry lag: one XNYS session from completed decision session to selected entry open.
- Exit: after five complete holding sessions at the next XNYS open; four/six only for the frozen
  robustness definitions.
- Maximum holding dependency: six sessions. Dependency purge: seven sessions, comprising the
  maximum six-session hold plus one-session decision/entry lag. Opening embargo: one session.
- Each annual Historical fold admits only signals whose complete entry and exit remain inside the
  fold. No carry-in position and no synthetic force-close are allowed. December signals that cannot
  complete inside the same fold are excluded by the frozen signal window and reported.
- One isolated normalized sleeve with initial capital `1.0`, at most one open position, no
  pyramiding, borrowing, cross-sleeve transfers, or evaluation-period rebalancing.
- Base cost per side: 5 bps slippage plus 1 bp fee; 12 bps total round trip.
- Stress cost per side: 20 bps slippage plus 2 bps fee; 44 bps total round trip.
- Entry and expiry are next-open market events. Missing next session is unfilled; no invented price
  is allowed. Canonical adverse intrabar handling remains pinned but no target/stop order is used.

## Method and stages

### 1. Preregistration

After the complete frozen summary is approved by `ochowei@gmail.com`, preregister only through the
workflow CLI. Do not transition to `running`, refresh ACWI, create trial sources, inspect outcomes,
or execute until separately authorized after preregistration.

### 2. Workflow-native source and Development

Create all formal source only under `src/trading/research_definitions/acwi-turn-of-month/`; never
add, rename, or repurpose `src/trading/experiments/`. The source must encode the exact calendar,
signal, entry, holding, expiry, data, workflow, and policy semantics above and capture all
outcome-relevant maintained orchestration source required by v002.

Capture immutable Development snapshots capped at 2020-12-31 and run all three selection candidates
plus the distinct baseline offline. All four valid observations must exist before any eligibility
or ranking. Apply the frozen gates and selection rule. If no candidate is eligible, stop with
Development `fail` without inspecting 2021+ outcome evidence.

If exactly one candidate is selected, materialize `selected-hold-four` and `selected-hold-six`
deterministically, record all six exact source/definition fingerprints, and obtain explicit
candidate-freeze and Historical-stage approval from `ochowei@gmail.com`. No Historical outcome may
be inspected before this approval.

### 3. Historical Evaluation and robustness

Before the first Historical outcome inspection, register the frozen Historical plan and complete
family universe using maintained qualification infrastructure:

- annual folds: 2021, 2022, 2023, 2024, 2025;
- maximum holding 6, execution lag 1, dependency purge 7, opening embargo 1;
- random seed `20260812`;
- 1,000 exposure-matched random-entry samples;
- 1,000 family-wise block-bootstrap repetitions with 20-session blocks;
- all six permanent trial identities, including failed/non-selected/robustness definitions.

Capture exact manifests through 2025-12-31, execute every family trial from immutable bundles, and
recompute the Historical Screen from maintained code. Required challenges are cash, the distinct
mid-month baseline, exposure-matched random entries, family-wise block-bootstrap adjustment, both
non-selected entry offsets, hold-four/hold-six perturbations, one additional session of entry delay,
strict stress costs, deterministic 10% missed entries keyed by SHA-256 of
`plan-id:trial-id:signal-date`, and per-fold regime/zero-signal reporting. No partial ranking or
replacement candidate is permitted.

### 4. Independent review and terminal scope

After every reachable planned stage has complete terminal evidence, update only `EVIDENCE.md`, move
the study to `awaiting-review`, and stop operator work. An independent reviewer using
`trading-evaluate-study` writes `CONCLUSION.md`, derives one allowed outcome, and completes the
study. Historical `pass` means only `shadow-eligible`; this study then terminates without Shadow
registration, activation, broker access, orders, private ledger data, or live authorization.

## Metrics and outcome rules

### Development eligibility and selection

Development metrics use only 2009-2020 canonical base/stress daily equity and completed trades.
Every candidate must pass all gates:

- at least 20 completed trades and at least one completed trade in every Development year;
- base compounded return > 0 and base profit factor > 1.10;
- stress compounded return > 0 and stress profit factor > 1.00;
- stress maximum drawdown no worse than `-15%`;
- no single calendar year contributes more than 50% of completed trades or positive profit;
- base-net daily-equity Sharpe strictly exceeds the mid-month baseline by at least `0.15`;
- exact data/definition/policy/workflow/orchestration/result identities validate with no
  unclassified parity difference.

Among eligible candidates, select exactly one by descending canonical sleeve base-net daily-equity
Sharpe. Resolve an exact tie by lexicographic stable source identity. Invalid or stale required
candidate evidence stops selection; it does not permit partial ranking. No eligible candidate or
trial-budget exhaustion is terminal `fail`.

### Historical and robustness gates

The selected candidate must satisfy every v002 workflow floor and the stricter frozen 15% stress
drawdown limit:

- five complete annual folds, at least 20 completed trades, at least 3 traded folds, and at least
  60% positive traded folds;
- base compounded return > 0 and profit factor > 1.10;
- stress compounded return > 0 and profit factor > 1.00;
- stress maximum drawdown >= `-15%`;
- no fold contributes more than 50% of total completed trades or total positive profit;
- candidate compounded return strictly exceeds cash, the mid-month baseline, and the 90th
  percentile of exposure-matched random entries;
- family-wise block-bootstrap adjusted confidence >= 90% across the complete six-trial family;
- both entry-offset perturbations and hold-four/hold-six challenges retain positive base and stress
  compounded return and stress drawdown >= `-15%`;
- one-session delayed entry and deterministic missed-entry challenges retain positive stress
  compounded return and stress drawdown >= `-15%`;
- every fold, excluded cross-boundary signal, zero-signal fold, unfilled entry, and regime label
  remains visible, and all immutable identities and checksums verify.

Terminal outcomes:

- `pass`: Development selection and every complete Historical/robustness gate pass; means only
  `shadow-eligible`.
- `fail`: any complete Development, Historical, benchmark, selection-adjustment, or robustness
  gate fails, or the trial budget is exhausted without an eligible candidate.
- `insufficient-evidence`: unavailable for these fixed Development/Historical gates; it may apply
  only to a later, separately registered prospective Shadow stage outside this study.
- `indeterminate`: required approval, identity, immutable artifact, complete source capture,
  checksum, complete commit SHA, data integrity, family universe, or reproducible evidence is
  missing/conflicting and cannot be repaired without changing the frozen design.

## Deviations and stopping rules

After preregistration, never edit `HYPOTHESIS.md` or `PLAN.md`. Do not change the ticker, data-role
dates, calendar-offset definitions, candidate inventory, `maximum_trials`, selection rule,
baseline, costs, holding/dependency semantics, thresholds, randomization, stopping rules, or outcome
rules. Do not tune from Development failures, inspect Historical early, reuse Historical after
failure, hide trials, weaken gates, create partial rankings, call a broker, submit orders, claim
live authorization, or store private trading data under `workflows/`.

Pause on provider/data incompleteness, digest drift, dirty outcome-relevant source not fully
captured, evidence corruption, trial-family drift, missing human advancement approval, or a
workflow/policy governance defect. Repair only the same frozen evidence. A strategy, data-role,
execution, or plan meaning change requires cancellation and a new study with exact `revisits`;
released workflow/policy defects require change/version governance and must never be patched in
place.

Terminate on Development or Historical `fail`, unrecoverable `indeterminate`, trial-budget
exhaustion, substantive post-freeze definition change, or explicit human-owner stop. Every formal
observation records exact workflow and policy releases, composite policy-set identity, immutable
data and Research Definition Snapshots, outcome-relevant orchestration identity, complete Git HEAD
and captured dirty status/diff, command, result identity/path, and SHA-256 checksum. Study evidence
stores exact references only and no raw private data.
