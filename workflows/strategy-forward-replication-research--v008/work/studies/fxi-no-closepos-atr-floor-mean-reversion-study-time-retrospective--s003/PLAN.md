# Plan: FXI No-ClosePos ATR-Floor Mean-Reversion Study-Time Retrospective Evaluation

## Inputs and frozen identities

### Governance, lineage, and authority

- Study: `strategy-forward-replication-research@v008/S003` at
  `workflows/strategy-forward-replication-research--v008/work/studies/fxi-no-closepos-atr-floor-mean-reversion-study-time-retrospective--s003`.
- Route: `study-time-retrospective` under capability `study-time-retrospective-v1`.
- Exact `revisits` target:
  `workflows/strategy-forward-replication-research--v008/work/studies/fxi-volume-stratified-atr-floor-mean-reversion-study-time-retrospective--s002`.
- Workflow `RELEASE.json` SHA-256:
  `760199711fe858e07a33f9990da22a48f1ded6bfbba8c1127e6647bc48b46f50`.
- Workflow definition SHA-256:
  `416600c848bb63cf86c49f986c225fe87f76547fd8089b4495d6349976de24b4`.
- Draft-preparation Git HEAD: `74d4197bfc9a81d053068b5552dd20c73fe9c6bc`.
- Composite policy-set identity:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Proposed human research owner and later approver: `ochowei@gmail.com`.
- Researcher identity: `codex-primary-researcher-fxi-mean-reversion`.

The study remains `draft`. These files do not grant preregistration, Development,
candidate-freeze, Evaluation, Shadow, broker, or order authority. Every later authority requires
its own guarded current-time action. S001 and S002 are completed, validated, and read-only lineage
evidence; this study does not modify either predecessor.

The 2026-08-18 freshness check reports that the FXI AI context and most cross-asset knowledge use
data through 2025-12-31, about eight months old. This study records that limitation and does not
refresh data or inspect outcomes during planning.

### Released policy pins

| Family | Version | Release digest | Config digest |
| --- | --- | --- | --- |
| `us-equity-market` | `v002` | `9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978` | `7acaaf98ac31a31fcc5f8603e8a4df2232ea25c0adb6c6372da24191fb29e44d` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` | `beb47a951fbae842ebea79353f6c31dcf784a74537d48d1e8e8c696d0618ec28` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` | `fd7cbb7bfd77887b557c2c9075124adb6a1b77e6789bd6cf91971e44646be5f8` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` | `0c1f786cfe686ec9633c6d0ff70d2d1fab9053fd5040c4f0487c6d047aabb9dc` |

No implicit `latest` workflow or policy is allowed. Every formal snapshot, observation,
qualification event, challenge artifact, and terminal package must bind these exact identities.

### Data roles, provenance, and calendar

- Sole market-data dependency: Yahoo `auto_adjust=True` adjusted daily OHLCV for `FXI`.
- Calendar/session authority: released `us-equity-market@v002` XNYS sessions.
- Evidence classification: `known-contaminated`.
- Trial-history disclosure: `trial_history_complete=false` and
  `prior_selection_history_incomplete=true`; neither may be relabelled complete.
- Warmup: 2013-11-06 through 2014-12-31, observation-only. This supplies more than the 252 prior
  completed sessions required by the volume feature before the first Development decision.
- Development: complete calendar years 2015 through 2019.
- Quarantine: every 2020 session.
- Study-time retrospective Evaluation: five complete annual folds, 2021 through 2025.
- Shadow and live use: prohibited.

The exact-study planner must derive and freeze every session inventory. Warmup can compute
indicators and volume references but cannot create signals, cooldown, positions, fills, P&L, or
performance. Evaluation trades belong to their signal-date fold and must enter and exit inside that
fold. Purge the final 21 completed sessions from signal generation where required for the maximum
holding plus execution lag, and apply the pinned one-session opening embargo. No role may overlap,
be reassigned, or contribute carry-in positions.

All family members must use one exact full-refresh generation through 2025-12-31. Corporate-action
or provider revisions are handled only by freezing that one canonical generation: no artifact may
stitch volume from another cache generation, perform post hoc rebasing, or fetch a separate action
feed. If common-generation identity or internally consistent adjusted OHLCV cannot be proved,
volume coverage is not complete and evidence fails closed.

### Frozen six-member family

`maximum_trials=6`. Only the first identity is eligible for selection. The baseline and four
robustness members cannot win or replace it. Every viewed outcome-relevant semantic definition
counts against the budget; rerunning the same fingerprint adds an observation, not a trial.

| Identity | Role | Source SHA-256 |
| --- | --- | --- |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-atr-floor-candidate` | selection candidate | `9e4d355b27517f389d1daf34c76b0bfbfa28cfd10f206d18de64f2f3a1810f6b` |
| `fxi-no-closepos-atr-floor-mean-reversion/pullback-wr-baseline` | distinct family baseline | `f2a80bcb33700832a20b80af7b71c247db58da2c258a5fb82b562035e8dd6bb9` |
| `fxi-no-closepos-atr-floor-mean-reversion/s002-closepos-reference` | robustness-only exact S002 candidate | `149714e85b1e922ba310e5db944b07691401c51751cefdf4a8ac40db9fd3a18c` |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-atr-floor-1p10-robustness` | robustness only | `d9a5a0d95e4537c5b1c8045ce9b8e9ce4b71aa29640b266a27654bc52851e7d9` |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-cooldown-7-robustness` | robustness only | `0e685eb68323bf38c5de9082cd204791f45e503473706857ef6a191d7f6d8de3` |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-delay-one-session-robustness` | robustness only | `a9e5895399b23894a878dc0823ca9590f79c36772242c954f24f8731a4269fcb` |

Shared runtime: `src/trading/research_definitions/fxi_mean_reversion.py`, SHA-256
`e091fce410709eeceb9b45f5bb753154866eff07f0a1bc0484611133367266d5`.
Provider-free definition tests:
`tests/test_workflow_native_fxi_mean_reversion_definition.py`, SHA-256
`1a875287d22046d8cda3d9cd9d873a8d15f3b6399cd039034054d9aeb1a316df`.

The candidate is Development-eligible only if all six observations are valid and reproducible, it
completes at least 20 trades across at least three Development years, base and stress compounded
returns are positive, base profit factor exceeds 1.1, stress profit factor exceeds 1.0, and stress
maximum drawdown is at most 20%. It is selected if and only if eligible. Volume and signal-funnel
diagnostics cannot affect this decision. Otherwise the governed no-candidate terminal-evidence path
applies.

### Signal, execution, cooldown, and sleeve

- `Pullback=(adjusted_close-inclusive_10_session_high)/inclusive_10_session_high`, inclusively
  bounded from -12% through -5%.
- Williams %R(10) must be at or below -80; a zero rolling high-low range maps to -50.
- The selection candidate has no ClosePos condition. Only the exact S002 reference uses
  `ClosePos=(close-low)/(high-low) >= 0.40`; its zero-range value is 0.50.
- True range is the maximum of high-low, absolute high-prior-close, and absolute low-prior-close.
  Simple `ATR(5)/ATR(20)` must be strictly above 1.05. There is no upper bound.
- Accepted candidate signals use a ten-completed-session cooldown from the previous accepted raw
  signal. The cooldown perturbation uses seven sessions and is non-selectable.
- Entry is market at the next completed XNYS open. The +5.5% Day limit target and -5.0% GTC
  stop-market become active after entry on the entry session. An unresolved position exits at the
  open after twenty completed holding sessions.
- Same-session ambiguity, gaps, unfilled orders, pessimistic ordering, fees, and slippage follow
  `canonical-execution@v001` and the other pinned policies without local override.
- The canonical isolated sleeve uses capital 1.0, fractional quantity, one position at a time, no
  leverage, pyramiding, borrowing, rebalancing, or cross-sleeve transfer.

### Provider-free Development signal funnel

The tracked Development gate must contain a replayable, ordered signal funnel for the sole
candidate over the exact Development decision inventory:

1. completed decision sessions after warmup and boundary rules;
2. sessions satisfying inclusive pullback `[-12%, -5%]`;
3. the preceding set also satisfying Williams %R(10) `<= -80`;
4. the preceding set also satisfying simple `ATR(5)/ATR(20) > 1.05`;
5. the preceding set accepted after the fixed ten-session raw-signal cooldown, with suppressed
   dates and their prior accepted-signal identity retained;
6. accepted raw candidates after canonical one-position conflict handling, with every skipped
   candidate and `position_already_open` reason retained;
7. executable entries after next-open availability and policy handling, including every unfilled
   reason; and
8. completed canonical-sleeve trades, separately retaining any still-open candidate.

Every stage records the ordered session/trade identities, exact count, and SHA-256 of its canonical
payload. Each downstream identity must be a subset or policy-derived transform of the prior stage,
and replay must use the same frozen primary data blob, definition fingerprint, and formal
observation. The exact S002 reference additionally reports the fixed `ClosePos >= 0.40` exclusion
between stages 3 and 4 as a separate diagnostic: ordered dates satisfying pullback+WR+ATR floor but
failing only that registered threshold. It cannot introduce another ClosePos threshold, change the
candidate funnel, alter eligibility/ranking, or supply a replacement candidate. No outcome-derived
threshold, post-hoc grouping, provider call, or Evaluation input is permitted.

### Frozen volume stability method

For every completed candidate trade, use its signal session's `Volume` only after that session is
completed. The reference is exactly the preceding 252 completed XNYS sessions in the same frozen
OHLCV generation and excludes the signal session. Let `L` be the number of reference volumes
strictly below signal volume and `E` the number equal to it. The percentile is
`(L + 0.5 * E) / 252`. Low is `<1/3`, normal is `>=1/3 and <=2/3`, and high is `>2/3`.

Signal and all 252 reference volumes must be present, finite, and strictly positive. A valid zero
volume is not silently imputed: that trade remains unclassified and the 100% coverage gate fails.
Missing/non-finite data, mixed generation identity, or unverified corporate-action/provider
revision integrity is an evidence-integrity problem. Ties use the fixed mid-rank formula; no jitter,
later session, outcome, or provider call is permitted.

The `market-regimes` artifact must preserve for every completed trade: signal date, annual fold,
signal volume, reference start/end, `L`, `E`, percentile, tercile, base/stress net trade P&L, and
the exact data-blob identity. It must expose counts, fold coverage, completed-trade shares, and the
sum of `max(base_net_trade_pnl, 0)` by tercile. The high-tercile exclusion calculation keeps the
original accepted-signal, cooldown, position-conflict, and trade ledger fixed; high-tercile trade
intervals earn cash and cannot admit replacement signals. It then rechains the remaining exact
trade ledger under base and stress costs.

Volume may not enter a definition config, signal mask, Development gate, candidate ranking,
bootstrap selection adjustment, family identity, or entry decision. It is challenge evidence only.

### Costs, benchmarks, and legal challenge mapping

- Base costs: 5 bps entry slippage, 5 bps exit slippage, and 1 bp fee per side.
- Stress/higher-cost costs: 20 bps entry slippage, 20 bps exit slippage, and 2 bps fee per side.
- Random-entry and deterministic missed-entry seed: `20260818`.
- Exposure-matched random benchmark: 1,000 samples.
- Complete-family block bootstrap: 1,000 repetitions with twenty-session blocks.
- Missed-entry challenge: deterministically omit 10% of otherwise executable candidate entries.

The validator accepts exactly nine challenge IDs. No volume- or funnel-specific tenth ID is
introduced. Volume terciles are an applicable market-regime dimension and are frozen inside the
existing `market-regimes` method target together with the five annual folds.
`parameter-perturbation` contains the exact S002 ClosePos-gated reference, the no-ClosePos ATR-floor
1.10 member, and the no-ClosePos cooldown-7 member. The exact delayed-entry robustness definition
maps only to the separate `delayed-entry` method target. The signal funnel is Development evidence,
not a challenge or a selection dimension. Every challenge has a unique content-addressed artifact
and raw values sufficient to recompute its typed gate.

## Method and stages

### 1. Draft and preregistration readiness

While draft, verify v008, predecessor completion, policies, exact source hashes, family, calendar,
stale-context warning, known contamination, funnel/volume semantics, registries, and challenge
mapping. Run provider-free tests only. Do not refresh data, create a snapshot, run a definition,
calculate Development/Evaluation metrics, rank trials, or mutate a registry.

Show the complete frozen summary to the human owner. Only explicit current-time approval may invoke
guarded preregistration. After preregistration, `HYPOTHESIS.md`, `PLAN.md`, and
`QUALIFICATION_SPEC.json` are immutable.

### 2. Development authorization and execution

After preregistration, obtain separate Development-only approval through the guarded CLI. Capture
exact Research Definition Snapshots under v008 and execute all six definitions only on 2015-2019
Development sessions with immutable manifests and formal offline observations. Preserve complete
family history, the provider-free signal funnel, and the deterministic eligibility decision. Do
not compute Evaluation volume gates or inspect 2021-2025 output during Development.

### 3. Candidate freeze

If the sole no-ClosePos candidate is eligible, prepare the guarded selection object containing
exactly `selected_candidate`, `family_baseline`, and ordered `complete_family`; each member has only
`source_identity`, `trial_id`, and `definition_fingerprint`. Obtain separate current-time owner
approval and use the add-only freeze command. Never hand-author or repair `CANDIDATE_FREEZE.json`.

If Development produces no candidate, do not create a freeze, plan, or screen. Prepare the tracked
registry-absence evidence required for independent review. The baseline or a robustness member may
not substitute even if it has at least 20 trades.

### 4. Provider-free readiness and qualification registration

With an approved freeze, compile the exact study using
`trading qualification plan register-study --study <study-path> --dry-run`. It must reproduce the
route, policies, six sources, shared runtime, calendar, candidate, baseline, costs, benchmarks,
volume method, challenge mapping, and incomplete-history disclosures without provider access or
registry mutation.

Registry mutation requires separate approval and a truthful contamination declaration. The
guarded transaction establishes one current-time `retrospective_selection_checkpoint`, registers
missing outcome-free identities at real current time, freezes the family, and appends one plan.

### 5. Evaluation execution and frozen screen

Evaluation requires separate narrow authority. Capture one eligible full-refresh generation
through 2025-12-31 for the first member; every other member reuses it provider-free. Run each exact
definition offline with one valid manifest and succeeded formal observation covering all frozen
Evaluation sessions.

The screen recomputes all fourteen shared gates and nine distinct challenge gates. The
`market-regimes` artifact computes the preregistered annual and volume-tercile evidence from the
same candidate ledger only after freeze; it cannot feed back into signals or ranking. Do not tune,
rerank, omit a member, replace the baseline, add a seventh identity, or reinterpret a failed gate.

Publish the content-addressed qualification snapshot and Development/challenge artifacts only in
their canonical tracked namespaces. Build `TERMINAL_EVIDENCE.json`, update only `EVIDENCE.md`, and
leave `CONCLUSION.md` untouched.

### 6. Independent review

After complete evidence, transition only to `awaiting-review`. An independent reviewer applies the
fixed terminal mapping. This study ends at a retrospective disposition and cannot register Shadow
or create any trading authority.

## Metrics and outcome rules

The fourteen conjunctive shared screen gates are:

1. at least 20 completed trades;
2. at least three traded folds;
3. at least 60% positive traded folds;
4. chained base compounded return greater than zero;
5. chained base profit factor greater than 1.1;
6. chained stress compounded return greater than zero;
7. chained stress profit factor greater than 1.0;
8. stress maximum drawdown at most 20%;
9. no fold above 50% of completed trades;
10. no fold above 50% of base-net positive profit;
11. candidate base return greater than cash;
12. candidate base daily-equity Sharpe at least 0.10 above the baseline;
13. candidate base return greater than the 90th percentile exposure-matched random return; and
14. complete-family block-bootstrap selection confidence at least 90%.

The `market-regimes` composite gate additionally requires 100% volume-feature coverage; at least
two terciles each with at least five completed trades across at least two Evaluation folds; no
tercile above 50% of completed trades or base-net positive profit; and chained base and stress
returns greater than zero after fixed-ledger high-tercile exclusion. The artifact also retains all
five annual folds, including zero-signal folds.

The `parameter-perturbation` gate requires valid exact evidence for the S002 reference and requires
the ATR-floor 1.10 and cooldown-7 variants each to preserve positive base/stress return, base profit
factor above 1.1, stress profit factor above 1.0, and stress drawdown at most 20%. The S002 reference
is diagnostic and identity-binding, not a replacement or an independently selectable candidate.
Delayed entry, higher costs, canonical worse fills, and missed entries must each preserve their
applicable positive-return, profit-factor, and 20% stress-drawdown constraints. Composite artifacts
must expose every underlying number and deterministic conjunction.

Terminal interpretation is fixed:

- `pass` plus `retrospectively-supported`: every identity and gate passes; no promotion follows.
- `fail` plus `development-selection-failed`: trustworthy Development has no eligible candidate,
  no freeze/plan/screen exists, and exact registry-absence evidence is complete.
- `fail` plus `retrospective-screen-failed`: the complete canonical screen has a failed frozen gate.
- `indeterminate`: identity, classification, approval, data, corporate-action/generation integrity,
  family, artifact, or registry replay cannot support a decision; `decision_stage` identifies it.
- `insufficient-evidence`: prohibited for this fixed historical checkpoint.

## Deviations and stopping rules

Stop and record any missing, stale, conflicting, mixed-generation, non-replayable, or incorrectly
bound source, policy, manifest, calendar, registry event, funnel stage, volume feature, challenge
artifact, or approval. Never impute volume, change tercile boundaries, query another provider, add
an outcome-derived funnel threshold, or turn the volume challenge into an entry rule.

After preregistration, never change the hypothesis, route, calendar, family, parameters, baseline,
funnel contract, volume formula, costs, metrics, thresholds, seeds, challenge targets, evidence
classification, or outcome mapping. Never use 2021-2025 outcomes to tune or replace the candidate,
hide trials, produce partial ranking, use mutable `latest`, call a broker, create orders, or claim
live authority.

Pause only through the guarded lifecycle with a concrete reason. If the frozen design must change,
cancel and initialize the next CLI-allocated successor with exact `revisits`. Terminate after a
governed Development no-candidate result, a complete retrospective screen, irrecoverable evidence
failure, trial-budget exhaustion, or explicit human stop.
