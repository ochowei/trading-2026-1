# Plan: SCHD Down-Streak Mean-Reversion Governance Pilot

## Inputs and frozen identities

### Governance

- Workflow: `strategy-forward-replication-research@v001`
- Workflow path: `workflows/strategy-forward-replication-research--v001`
- Workflow `RELEASE.json` SHA-256:
  `db463628c6174934b4e342031466afce9d543a18e4af5b9c0b6cfe8e604b8896`
- Workflow definition SHA-256:
  `8eedc7ff3374254b43c4c5926a1363cf0134a9912e5f8966a3dcbd12ba99997a`
- Study: `strategy-forward-replication-research@v001/S001`
- Human research owner and preregistration approver: `ochowei@gmail.com`
- Creator: `ochowei@gmail.com`
- Execution agent identity recorded at execution time; it cannot review or complete the study.
- Independent reviewer must not have participated in topic selection, plan authoring, source authoring,
  data execution, evidence production, or candidate freeze.

### Exact policy set

Composite policy-set identity:
`4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.

| Family | Release | `RELEASE.json` SHA-256 | `policy.yaml` SHA-256 |
| --- | --- | --- | --- |
| `us-equity-market` | `v001` | `7df1e266aa72ccfaca3efa3e490ad6234f300bb0bfc4e31b3dd3c85ab93de542` | `c2944014942674483d326aa45b34adcc9e8629bcfb53a315b2d029a84a547d10` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` | `beb47a951fbae842ebea79353f6c31dcf784a74537d48d1e8e8c696d0618ec28` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` | `fd7cbb7bfd77887b557c2c9075124adb6a1b77e6789bd6cf91971e44646be5f8` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` | `0c1f786cfe686ec9633c6d0ff70d2d1fab9053fd5040c4f0487c6d047aabb9dc` |

Definition capture and every formal run must re-resolve these exact releases and composite identity;
implicit latest, digest drift, missing family, or duplicate family is `indeterminate` and stops work.

### Market data and data roles

- Primary series: Yahoo auto-adjusted daily OHLCV for `SCHD`, XNYS calendar, no auxiliary series.
- Signal Decision Time: after a completed daily session under `us-equity-market@v001`.
- 2022-01-01 through 2022-12-31: warmup only; never contributes performance.
- 2023-01-01 through 2025-12-31: Development selection evidence.
- 2026-01-01 through 2026-12-31: Development-role quarantine. It may support operational freshness
  later but cannot change the frozen candidate, gates, or selection made from 2023–2025.
- 2027-01-01 through 2031-12-31: five consecutive, non-overlapping future-only annual Historical
  Evaluation folds. No outcome from these folds may be inspected before the candidate freeze.
- Shadow: outside this pilot. A later separately authorized action may register prospective Shadow
  only after a passing persisted Historical Screen.
- Every formal observation uses a full refresh capped at its frozen decision session, an immutable
  market-data snapshot, and an immutable Research Definition Snapshot.

The repository cross-asset context available at design time has `data_through: 2025-12-31` and is
older than six months at preregistration. It was used only for general safety constraints, not to
inspect SCHD outcomes. The future-only 2027–2031 folds are the required revalidation boundary.

### Trial budget and inventory

`maximum_trials=5`. A semantic fingerprint counts once; rerunning the exact fingerprint is another
observation, not another trial. Failed, removed, unfilled, or abandoned observations remain visible.

| Stable source identity | Role | Frozen semantics |
| --- | --- | --- |
| `schd-down-streak-reversion/two-down` | selection candidate | two consecutive down closes; next-open entry; five-session hold; next-open expiry |
| `schd-down-streak-reversion/three-down` | selection candidate | three consecutive down closes; otherwise identical |
| `schd-down-streak-reversion/periodic-baseline` | distinct simple baseline | no signal filter; repeated five-session exposure under the same sleeve/execution rules |
| `schd-down-streak-reversion/selected-hold-four` | robustness-only | selected streak threshold; four-session hold; never eligible to replace the candidate |
| `schd-down-streak-reversion/selected-hold-six` | robustness-only | selected streak threshold; six-session hold; never eligible to replace the candidate |

Only the first two form the candidate set. The baseline and robustness trials cannot win selection.
The two robustness definitions are materialized only after candidate freeze using the deterministic
selected threshold and before any Evaluation outcome is inspected.

### Execution dependencies and costs

- Entry lag: one XNYS session; entry is next open market.
- Exit: fixed expiry after five complete holding sessions, at the next open market.
- Maximum holding: five sessions for the selected definition; six for the preregistered upper
  perturbation only.
- Dependency purge: seven sessions (maximum six-session challenge holding plus one-session lag).
- Opening embargo: one session. No carry-in position; candidates that cannot exit inside a fold are
  excluded by the frozen signal window, not force-closed.
- One isolated normalized sleeve, initial capital `1.0`, at most one open position, no pyramiding,
  borrowing, cross-sleeve transfers, or evaluation-period rebalancing.
- Base costs per side: entry slippage 5 bps, exit slippage 5 bps, fee 1 bp.
- Stress costs per side: entry slippage 20 bps, exit slippage 20 bps, fee 2 bps.
- Intrabar ambiguity is not used because all entries/exits are next-open market events. Missing next
  session is unfilled; no invented price is allowed.

## Method and stages

### 1. Preregistration

Before any SCHD refresh, execution, or outcome inspection, freeze this hypothesis and plan through:

```bash
uv run trading workflow study preregister \
  workflows/strategy-forward-replication-research--v001/work/studies/\
schd-down-streak-reversion-pilot--s001 --approved-by ochowei@gmail.com
uv run trading workflow study transition \
  workflows/strategy-forward-replication-research--v001/work/studies/\
schd-down-streak-reversion-pilot--s001 --to running --by codex-primary-execution-agent
```

### 2. Development and candidate freeze

For each of `two-down`, `three-down`, and `periodic-baseline`, capture the exact policy-bound
definition and a full-refresh immutable SCHD snapshot capped at 2025-12-31, then execute offline:

```bash
uv run trading research snapshot <family/trial> \
  --workflow workflows/strategy-forward-replication-research--v001 \
  --decision 2025-12-31
uv run trading research run <family/trial> \
  --workflow workflows/strategy-forward-replication-research--v001 \
  --manifest results/<result-name>/<snapshot-id>.snapshot.json --offline
```

All three valid Development results must exist before any ranking. Apply the frozen eligibility and
selection rules below. If none is eligible or the monotonic claim fails, stop with Development
`fail`; do not inspect 2027+ data. If supported, select exactly one candidate by the frozen rule,
materialize the two robustness-only definitions, record exact fingerprints, and obtain explicit
candidate-freeze/stage-advancement approval from `ochowei@gmail.com` before Historical work.

### 3. Future-only Historical Evaluation and robustness

Register a Forward Selection Epoch and Historical plan before the first 2027 outcome, with
evaluation years 2027–2031, maximum holding 6, execution lag 1, dependency 7, embargo 1, random seed
`20260812`, 1,000 random samples, 1,000 bootstrap repetitions, and 20-session blocks. Freeze all five
formal trial identities in the family universe. After the final 2031 fold completes, capture exact
manifests through the final session, rerun every family trial from immutable bundles, and compute the
Historical Screen from maintained qualification code. No partial ranking is allowed.

Required challenges are cash, the frozen periodic baseline, 1,000 exposure-matched random entries,
family-wise block-bootstrap adjustment over all five trials, holding 4/6 perturbations, one-session
additional entry delay, stress costs, deterministic 10% missed entries keyed by SHA-256 of
`plan-id:trial-id:signal-date`, and per-fold regime reporting. Challenges only support or falsify the
selected candidate and never produce a replacement.

### 4. Independent review and completion

After all reachable planned stages have terminal evidence, fill only `EVIDENCE.md`, transition to
`awaiting-review`, and stop execution work. A sub-agent that did not participate in design or
execution must use `trading-evaluate-study`, write `CONCLUSION.md`, choose the evidence-derived
outcome, and run the completion CLI. A Historical `pass` means only `shadow-eligible`; the study is
then terminal for this pilot by design and performs no Shadow registration or activation.

## Metrics and outcome rules

### Development eligibility and selection

Development metrics use only 2023–2025 canonical base/stress daily-equity and completed trades.
Each candidate must pass every gate:

- at least 20 completed trades and at least one completed trade in each Development year;
- base compounded return greater than 0 and base profit factor greater than 1.10;
- stress compounded return greater than 0 and stress profit factor greater than 1.00;
- stress maximum drawdown no worse than -15%;
- no single year contributes more than 50% of completed trades or positive profit;
- base-net Sharpe strictly exceeds the periodic baseline base-net Sharpe by at least 0.25;
- exact data/definition/policy/result identities validate, with no unclassified parity difference.

The claim additionally requires `three-down` base-net Sharpe to be strictly greater than
`two-down`. Among eligible candidates, select highest base-net Sharpe; an exact tie is resolved by
lexicographic stable source identity. Failed candidates remain recorded. No eligible candidate or a
failed monotonic claim is terminal `fail`.

### Historical and robustness gates

The selected candidate must pass every released workflow floor, with the stricter frozen stress
drawdown limit of 15%:

- five complete annual folds; at least 20 completed trades; at least 3 traded folds;
- at least 60% positive traded folds;
- base compounded return > 0 and profit factor > 1.10;
- stress compounded return > 0 and profit factor > 1.00;
- stress maximum drawdown >= -15%;
- every trade/profit fold concentration <= 50%;
- candidate compounded return strictly exceeds cash, periodic baseline, and the 90th percentile of
  exposure-matched random entries;
- family-wise block-bootstrap adjusted confidence >= 90%;
- both holding perturbations retain positive base/stress return and stress drawdown >= -15%;
- delayed-entry and deterministic missed-entry challenges retain positive stress return and stress
  drawdown >= -15%;
- all folds, including zero-signal folds and regime labels, remain visible.

Terminal outcome rules:

- `pass`: Development claim and every Historical/robustness gate pass; means only
  `shadow-eligible`.
- `fail`: any complete Development, Historical, benchmark, selection-adjustment, or robustness gate
  fails, or the trial budget is exhausted without an eligible candidate.
- `insufficient-evidence`: not available for a fixed Development/Historical gate in this pilot; it
  would apply only to a separately continued prospective Shadow stage.
- `indeterminate`: required identity, immutable artifact, approval, checksum, complete commit SHA,
  data integrity, complete family universe, or reproducible evidence is missing/conflicting and
  cannot be repaired without changing the frozen design.

## Deviations and stopping rules

After preregistration, do not change `HYPOTHESIS.md` or `PLAN.md`. Do not change ticker, dates/data
roles, candidate inventory, `maximum_trials`, selection rule, baseline, costs, dependencies,
thresholds, randomization, stopping rules, or outcome rules. Do not tune from Development failures,
inspect Evaluation early, reuse Evaluation after failure, hide trials, weaken gates, create partial
rankings, call a broker, submit orders, claim live authorization, or write private trading data into
the study.

Pause on provider/data incompleteness, digest drift, dirty source not fully captured, evidence
corruption, trial-family drift, missing human advancement approval, or a governance defect. Repair
only the same evidence under the frozen plan. If design meaning must change, cancel and create a new
study with exact `revisits`. If a released workflow/policy defect is found, leave the release
untouched and use `trading-author-workflow` change/version governance.

Terminate on Development or Historical `fail`, unrecoverable `indeterminate`, trial-budget
exhaustion, substantive post-freeze strategy change, or explicit human-owner stop. Every formal
observation records exact workflow/policy releases, composite policy-set identity, immutable data
and definition snapshots, complete Git HEAD plus captured dirty diff/status, command, result path,
result identity, and SHA-256 checksum. `EVIDENCE.md` stores only these exact references and no raw
private data.
