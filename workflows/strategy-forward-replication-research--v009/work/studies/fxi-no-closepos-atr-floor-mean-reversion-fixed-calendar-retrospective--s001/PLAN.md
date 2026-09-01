# Plan: FXI No-ClosePos ATR-Floor Mean-Reversion Fixed-Calendar Retrospective Study

## Inputs and frozen identities

- Workflow: `strategy-forward-replication-research@v009` at
  `workflows/strategy-forward-replication-research--v009`.
- Route: exactly `fixed-calendar-retrospective`.
- Revisited study:
  `workflows/strategy-forward-replication-research--v008/work/studies/fxi-no-closepos-atr-floor-mean-reversion-study-time-retrospective--s003`.
- Human research owner: supplied only at guarded preregistration; the draft does not infer or
  record approval.
- Research operator: `codex-primary-researcher-fxi-mean-reversion`.
- Trial registry: `results/registries/trial_registry.json`.
- Qualification registry: `state/qualification-registry.json`.
- Evidence classification: `known-contaminated`; `trial_history_complete=false` and
  `prior_selection_history_incomplete=true`.
- Policies and costs: the exact four releases, composite identity, config/release digests, and
  base/stress per-side costs frozen in `QUALIFICATION_SPEC.json`.
- Execution dependencies: maximum holding 20 sessions, execution lag 1, dependency window 21,
  embargo 1, and stress drawdown limit 20%.

The workflow-owned calendar is immutable:

| Role | Civil-date interval |
| --- | --- |
| Warmup only | 2013-01-01 through 2013-12-31 |
| Development | 2014-01-01 through 2018-12-31 |
| Quarantine | 2019-01-01 through 2019-12-31 |
| Historical Evaluation | 2020-01-01 through 2024-12-31, one fold per year |
| Retrospective execution replay | 2025-01-01 through 2025-12-31 |

The frozen family has `maximum_trials=6` and this exact order:

| Role | Research identity | Source SHA-256 |
| --- | --- | --- |
| sole selection candidate | `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-atr-floor-candidate` | `9e4d355b27517f389d1daf34c76b0bfbfa28cfd10f206d18de64f2f3a1810f6b` |
| distinct family baseline | `fxi-no-closepos-atr-floor-mean-reversion/pullback-wr-baseline` | `f2a80bcb33700832a20b80af7b71c247db58da2c258a5fb82b562035e8dd6bb9` |
| prior ClosePos reference | `fxi-no-closepos-atr-floor-mean-reversion/s002-closepos-reference` | `149714e85b1e922ba310e5db944b07691401c51751cefdf4a8ac40db9fd3a18c` |
| ATR-floor perturbation | `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-atr-floor-1p10-robustness` | `d9a5a0d95e4537c5b1c8045ce9b8e9ce4b71aa29640b266a27654bc52851e7d9` |
| cooldown perturbation | `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-cooldown-7-robustness` | `0e685eb68323bf38c5de9082cd204791f45e503473706857ef6a191d7f6d8de3` |
| delayed-entry perturbation | `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-delay-one-session-robustness` | `a9e5895399b23894a878dc0823ca9590f79c36772242c954f24f8731a4269fcb` |

All members share `src/trading/research_definitions/fxi_mean_reversion.py`, SHA-256
`e091fce410709eeceb9b45f5bb753154866eff07f0a1bc0484611133367266d5`.
Only the first member is selectable. The baseline and four robustness/reference members cannot
replace it regardless of their observed performance.

## Method and stages

### 1. Draft and preregistration readiness

Validate the active v009 `N04`/`N05` gate, exact workflow release, source hashes, policy pins,
fixed calendar, complete family, registries, typed gates, and all nine byte-exact
`fixed-challenge-v1` contracts. Provider-free validation may inspect definitions and schemas but
must not refresh data, create snapshots, execute a definition, inspect outcomes, or mutate a
registry.

Show the complete frozen claim, plan, and qualification specification to the human owner.
Preregister only through the guarded CLI after separate explicit approval. Preregistration makes
`HYPOTHESIS.md`, `PLAN.md`, and `QUALIFICATION_SPEC.json` immutable but does not authorize
Development.

### 2. Development

Obtain a separate Development-only authorization. Capture exact Research Definition Snapshots and
formal offline observations for all six definitions using only the 2013 warmup and 2014-2018
Development roles. Preserve all six observations, failures, trial identities, fingerprints, the
complete ranking, and the exact eligibility decision. Do not calculate or inspect 2020-2025
Evaluation or replay outcomes.

The sole candidate must satisfy the Development gates in `HYPOTHESIS.md`. Rank eligible selection
candidates by base-net daily-equity Sharpe with stable trial-ID tie-breaking; because the family
contains only one selection candidate, an ineligible result ends Development without substitution.

### 3. Candidate freeze

If Development yields an eligible candidate, prepare a selection JSON containing only
`selected_candidate`, `family_baseline`, and ordered `complete_family`, with each member limited to
`source_identity`, `trial_id`, and `definition_fingerprint`. Obtain separate current-time owner
approval and use the guarded freeze command. Do not hand-author `CANDIDATE_FREEZE.json`.

If no candidate is eligible, create no freeze, plan, or screen. Prepare the required tracked
Development gate and current-head qualification-absence evidence for independent review.

### 4. Provider-free fixed-calendar readiness

Run the exact-study compiler and `register-study --dry-run`. It must derive every expected XNYS
session from v009's civil dates, preserve all five disjoint roles, resolve the exact six-member
family and policies, and reproduce all frozen challenge contracts without provider access or
mutation.

Registry mutation requires separate current-time approval and a truthful `known-contaminated`
declaration. The recoverable transaction establishes a current-time retrospective selection
checkpoint, registers any missing outcome-free identities using their real registration times,
freezes the complete family, and appends one qualification plan.

### 5. Fixed Historical Evaluation and challenges

Obtain separate narrow Evaluation authority. Produce exact immutable offline observations for all
six members over the fixed 2020-2024 role inventory with one shared verified data generation.
Warmup may supply only declared dependencies; Development, quarantine, and replay sessions may
not contribute Evaluation signals, positions, fills, cooldown, P&L, benchmarks, or metrics.

Run the independent challenge-only operation first as a zero-mutation dry-run and then, only with
separate authority, as the guarded atomic publication. It must publish exactly nine distinct
content-addressed artifacts plus one manifest. It may not call a provider, execute a definition,
run the qualification screen implicitly, mutate either registry, or trust caller-supplied observed
values. The screen consumes the immutable artifacts and recomputes all shared gates.

### 6. Fixed 2025 retrospective execution replay

Proceed only after a persisted passing Evaluation screen. Obtain separate replay authority and
run the provider-free plan-bound operation over every expected 2025 XNYS session. Publish only
non-actionable paper proposals, simulated fills, ledger-style events, checkpoints, performance,
and historical drift evidence. Do not create Shadow registration, actual positions, broker calls,
orders, activation, or live authority.

### 7. Independent review

After all planned evidence is terminal, complete `EVIDENCE.md`, create exact terminal evidence,
leave `CONCLUSION.md` untouched, and transition only to `awaiting-review`. An independent reviewer
recomputes the terminal outcome from the frozen study and immutable evidence.

## Metrics and outcome rules

Development eligibility is the conjunction stated in `HYPOTHESIS.md`: at least 20 completed
trades across at least three Development years, positive base/stress return, base profit factor
above 1.1, stress profit factor above 1.0, stress drawdown no worse than 20%, and a valid complete
six-member family.

Fixed Evaluation must satisfy every v009 floor:

1. at least 20 completed trades;
2. at least three traded folds and at least 60% positive traded folds;
3. positive chained base return with profit factor above 1.1;
4. positive chained stress return with profit factor above 1.0;
5. stress maximum drawdown no worse than 20%;
6. no fold above 50% of trades or positive profit;
7. candidate return above cash and the frozen random-entry benchmark;
8. the distinct baseline challenge passes; and
9. complete-family block-bootstrap selection confidence is at least 90%.

Each of the nine challenge artifacts has the exact typed gate
`{"metric":"passed","operator":"=","threshold":true}`. The registered implementation—not
study prose—defines the observed boolean. The random seed is `20260901`; random samples and
bootstrap repetitions are each 1,000 with twenty-session blocks.

The 2025 replay must cover all expected sessions, complete at least 12 simulated fills, preserve
positive base and stress return, base and stress profit factor above 1.0, stress drawdown no worse
than 20%, and a passing historical critical-drift replay.

Terminal mapping is fixed:

- `pass` / `retrospectively-supported` only if Development selection, Evaluation, all nine
  challenges, and replay are complete and passing;
- `fail` / `development-selection-failed` when trustworthy Development yields no candidate and
  the exact absence proof is complete;
- stage-specific `fail` when a complete Evaluation, challenge, or replay gate fails;
- stage-specific `indeterminate` when identity, approval, data, calendar, policy, registry,
  artifact, or replay integrity cannot support a decision; and
- `insufficient-evidence` is prohibited.

## Deviations and stopping rules

After preregistration, never change the route, calendar, family, source bytes, candidate rules,
baseline, execution dependencies, costs, thresholds, seeds, registered method contracts,
classification, registry identities, or outcome mapping. Never tune from 2020-2025 outcomes,
replace a failed candidate, add a seventh trial, omit a family member, generate a partial ranking,
shift a year, extend 2025, use mutable `latest`, or claim promotional or trading authority.

Pause through the guarded lifecycle on any missing, stale, conflicting, mixed-generation,
non-replayable, incorrectly bound, partially published, or path-resolution evidence problem.
Technical recovery may restore only the same frozen bytes and exact committed transaction. A
semantic change requires cancellation and a new CLI-allocated study with an exact `revisits`
link. Terminate after governed Development no-candidate evidence, a complete Evaluation/replay
failure, irrecoverable integrity failure, trial-budget exhaustion, or explicit human stop.
