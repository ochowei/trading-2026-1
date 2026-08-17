# Plan: FXI ATR-Band Mean-Reversion Study-Time Retrospective Evaluation

## Inputs and frozen identities

### Governance, lineage, and authority

- Study: `strategy-forward-replication-research@v008/S001` at
  `workflows/strategy-forward-replication-research--v008/work/studies/fxi-atr-band-mean-reversion-study-time-retrospective--s001`.
- Route: `study-time-retrospective` under capability `study-time-retrospective-v1`.
- Exact `revisits` target:
  `workflows/strategy-forward-replication-research--v006/work/studies/fxi-atr-band-mean-reversion-retrospective-confirmation--s001`.
- Ancestral clean-study context:
  `workflows/strategy-forward-replication-research--v004/work/studies/fxi-atr-band-mean-reversion-forward-replication--s004`.
- Workflow `RELEASE.json` SHA-256:
  `760199711fe858e07a33f9990da22a48f1ded6bfbba8c1127e6647bc48b46f50`.
- Workflow definition SHA-256:
  `416600c848bb63cf86c49f986c225fe87f76547fd8089b4495d6349976de24b4`.
- Draft-preparation Git HEAD: `b0b9f17fa5aed542c69a681b00aae1599d35fbaa`.
- Composite policy-set identity:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Proposed human research owner and later approver: `ochowei@gmail.com`.
- Researcher identity: `codex-primary-researcher-fxi-mean-reversion`.

The study remains `draft`. Completing this document is not preregistration approval, Development
authorization, candidate-freeze approval, Evaluation authorization, or permission to inspect new
outcome artifacts. Each later authority requires its own guarded current-time action.

The 2026-08-17 freshness check reports most FXI and cross-asset knowledge through 2025-12-31,
approximately eight months old. This study records that limitation and does not refresh data or
inspect newer outcomes during planning.

### Released policy pins

| Family | Version | Release digest | Config digest |
| --- | --- | --- | --- |
| `us-equity-market` | `v002` | `9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978` | `7acaaf98ac31a31fcc5f8603e8a4df2232ea25c0adb6c6372da24191fb29e44d` |
| `firstrade-manual-trading` | `v001` | `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9` | `beb47a951fbae842ebea79353f6c31dcf784a74537d48d1e8e8c696d0618ec28` |
| `canonical-execution` | `v001` | `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925` | `fd7cbb7bfd77887b557c2c9075124adb6a1b77e6789bd6cf91971e44646be5f8` |
| `portfolio-risk` | `v001` | `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69` | `0c1f786cfe686ec9633c6d0ff70d2d1fab9053fd5040c4f0487c6d047aabb9dc` |

No implicit `latest` workflow or policy is allowed. Every formal snapshot, observation,
qualification event, challenge artifact, and terminal evidence package must bind these exact
identities.

### Data roles, provenance, and calendar

- Sole market-data dependency: Yahoo adjusted daily OHLCV for `FXI`.
- Calendar/session authority: released `us-equity-market@v002` XNYS sessions.
- Evidence classification: `known-contaminated`.
- Trial-history disclosure: incomplete legacy selection history and incomplete prior-selection
  history are both explicit; neither may be relabelled complete.
- Warmup bounds: 2013-11-06 through 2014-12-31, observation-only.
- Development: complete calendar years 2015 through 2019.
- Quarantine: every 2020 session.
- Study-time retrospective Evaluation: five complete annual folds, 2021 through 2025.
- Shadow and live use: prohibited.

The exact-study planner must deterministically derive and freeze all session inventories. Warmup
may compute indicators and dependencies but cannot create signals, cooldown, positions, fills,
P&L, or performance. Each Evaluation trade belongs to its signal-date fold and must enter and exit
inside that fold. Purge the final 21 completed sessions from signal generation where required to
prevent a position or dependency crossing a fold boundary; apply a one-session opening embargo.
No role may overlap or be reassigned.

The Evaluation interval may have influenced legacy definitions and interpretation. A new study or
new Agent does not restore unseen status. The classification can never be upgraded to
`verified-clean`; contrary evidence may only make the disclosure stricter.

### Frozen six-member family

`maximum_trials=6`. Only the first identity is eligible for selection. The baseline and four
robustness definitions cannot win or replace it. Every viewed outcome-relevant semantic definition
counts against the budget; rerunning an identical fingerprint adds an observation, not a trial.

| Identity | Role | Source SHA-256 |
| --- | --- | --- |
| `fxi-atr-band-mean-reversion/atr-band-candidate` | selection candidate | `a964aaf3e166becc24d4c66a9e00467bc77e05e8534da4b5b9ba6a0c4e67cc08` |
| `fxi-atr-band-mean-reversion/pullback-wr-baseline` | distinct family baseline | `3a838b5460befdb37de57a6744339a2d0b1101d4972bd34a81da1bcde4fc2ba4` |
| `fxi-atr-band-mean-reversion/atr-floor-1p10-robustness` | robustness only | `1eb19a0ed7cae4ccdbbdd1d81ae4af99b8a5379b2c7de3296d9119d029bf015f` |
| `fxi-atr-band-mean-reversion/atr-ceiling-1p30-robustness` | robustness only | `499f034fc8f3bc0207f5e4bebae669d0c45624390e241499d95cb44f3f3a31ed` |
| `fxi-atr-band-mean-reversion/hold-18-robustness` | robustness only | `8b60508760f6b16c79d5aa7348e59fa0d21609e37f61c561750f10e62f869021` |
| `fxi-atr-band-mean-reversion/delay-one-session-robustness` | robustness only | `784f91d0b40b9f3a6b071cfe2cb08a8ba135631244ff0f5b08ec2e26c93d8df2` |

Shared runtime:
`src/trading/research_definitions/fxi_mean_reversion.py` at SHA-256
`120df54dde206dd16f6293bff7bf4f042b396d8970fd644458eadba677e2be7e`.
Provider-free family tests are at
`tests/test_workflow_native_fxi_mean_reversion_definition.py`, SHA-256
`0b0ce3e54bcca876f39dc61676f575e1c31cf3b8a251945ddf3c991ef55a64fb`.

The candidate is eligible after Development only if its exact observation is valid and
reproducible, it completes at least 20 trades across at least three Development years, base and
stress compounded returns are positive, base profit factor exceeds 1.1, stress profit factor
exceeds 1.0, stress maximum drawdown is at most 20%, and every family member needed for the frozen
comparison is valid. Because there is only one selection-candidate identity, it is selected if and
only if eligible; no partial ranking or substitution is allowed. Otherwise the study follows the
governed no-candidate terminal-evidence path.

### Signal, execution, cooldown, and sleeve

- `Pullback=(adjusted_close-inclusive_10_session_high)/inclusive_10_session_high`, bounded
  inclusively from -12% through -5%.
- Williams %R(10) must be at or below -80; a zero high-low range maps to -50 and cannot pass.
- `ClosePos=(close-low)/(high-low)` must be at least 0.40; a zero range maps to 0.50.
- True range is the maximum of high-low, absolute high-prior-close, and absolute low-prior-close.
  Simple `ATR(5)/ATR(20)` must be strictly above 1.05 and at or below 1.35.
- Accepted signals use a ten-completed-session cooldown from the prior accepted signal.
- Entry is market at the next XNYS open. A +5.5% Day limit target and -5.0% GTC stop-market become
  active after entry on the entry session. Unresolved positions exit at the open after twenty
  completed holding sessions.
- Same-session ambiguity, gap fills, missing orders, and unfilled handling follow
  `canonical-execution@v001` pessimistically. No inferred fill is allowed.
- Canonical isolated sleeve uses capital 1.0, fractional quantity, one position at a time, no
  leverage, pyramiding, borrowing, rebalancing, or cross-sleeve transfer.

### Costs, benchmarks, and challenge identities

- Base costs: 5 bps entry slippage, 5 bps exit slippage, and 1 bp fee per side.
- Stress/higher-cost challenge: 20 bps entry slippage, 20 bps exit slippage, and 2 bps fee per side.
- Random-entry and deterministic missed-entry procedures use seed `20260817`.
- Exposure-matched random benchmark uses 1,000 samples.
- Complete-family block bootstrap uses 1,000 repetitions and twenty-session blocks.
- Missed-entry challenge deterministically omits 10% of otherwise executable candidate entries.
- Market-regime challenge treats the five annual Evaluation folds as frozen regimes and preserves
  zero-signal folds.

Each of the nine challenge artifacts must be distinct, content-addressed, and contain the raw
observed values needed to recompute its typed gate. For a composite boolean gate, the artifact must
contain every underlying numeric margin and the deterministic conjunction; a manifest-level
`passed` assertion is never sufficient.

## Method and stages

### 1. Draft and preregistration readiness

While the study is `draft`, verify the active v008 release, exact policy set, source digests,
calendar, stale-context warning, known-contamination classification, registries, and complete
six-member family. Run provider-free validation only. Do not refresh data, create snapshots, run a
definition, calculate Development/Evaluation metrics, rank trials, or mutate a registry.

Show the complete frozen summary to `ochowei@gmail.com`. Only a later explicit current-time human
approval may invoke guarded preregistration. After preregistration, `HYPOTHESIS.md`, `PLAN.md`, and
`QUALIFICATION_SPEC.json` are immutable.

### 2. Development authorization and execution

After preregistration, obtain a separate Development-only approval and transition through the
guarded workflow CLI. The resulting add-only `DEVELOPMENT_AUTHORIZATION.json` authorizes only
2015-2019 Development work.

Capture exact Research Definition Snapshots under v008 and the pinned policy set, then execute all
six definitions only on Development-eligible sessions using immutable manifests and formal offline
observations. Preserve complete family history, failures, tombstones, metrics, and the deterministic
eligibility decision. Do not inspect or serialize 2021-2025 Evaluation output during Development.

### 3. Candidate freeze

If the sole candidate is Development-eligible, prepare a selection JSON containing exactly
`selected_candidate`, `family_baseline`, and ordered `complete_family`. Each member contains only
`source_identity`, `trial_id`, and `definition_fingerprint`. Obtain separate current-time approval
from the human owner and use the guarded add-only candidate-freeze command. Never hand-author,
backdate, replace, or repair `CANDIDATE_FREEZE.json`.

If Development produces no eligible candidate, do not create candidate freeze, plan, or screen.
Prepare the exact tracked registry-absence evidence required for independent review.

### 4. Provider-free readiness and qualification registration

With an approved candidate freeze, compile the exact study using
`trading qualification plan register-study --study <study-path> --dry-run`. The compiler must
reproduce the route, policies, six sources, shared runtime, calendar, candidate, baseline, costs,
benchmarks, challenges, and incomplete-history disclosures without provider access, observation,
or registry mutation.

Registry mutation requires another separate operation approval and truthful current-time
contamination declaration. The guarded transaction must establish one
`retrospective_selection_checkpoint`, register any missing outcome-free identities at the real
current time, freeze the exact family, and append exactly one study-time plan. Retry must recover a
pending journal before accepting new inputs or timestamps.

### 5. Evaluation execution and frozen screen

Evaluation requires separate narrow authority after plan registration. Capture one eligible
full-refresh generation through the exact 2025-12-31 cutoff for the first family member; all other
members must reuse that same generation without provider access. Run each exact definition offline
with one valid manifest and one succeeded formal observation covering all frozen Evaluation
sessions.

The guarded screen must recompute the fourteen shared gates and the nine distinct challenge gates,
including annual/chained base and stress metrics, cash, baseline, exposure-matched random entries,
complete-family selection adjustment, both ATR-bound perturbations, delayed entry, higher costs,
worse fills, missed entries, fold/trade/profit concentration, and annual regimes. Do not tune,
rerank, omit a family member, replace the baseline, add a seventh definition, or reinterpret a
failed gate.

Publish the exact tracked qualification-registry snapshot under
`results/qualification-evidence/<sha256>.json` and each Development/challenge artifact under
`results/study-evidence/**`. Build `TERMINAL_EVIDENCE.json` from exact preregistration, spec,
candidate freeze, Development authorization, plan, sole canonical screen, registry checkpoint,
fourteen screen gates, and nine challenge artifacts. Record immutable identities and deviations in
`EVIDENCE.md`; do not write `CONCLUSION.md`.

### 6. Independent review

When all planned evidence is complete, transition only to `awaiting-review`. An independent
reviewer using `trading-evaluate-study` replays the authoritative registry and applies the frozen
mapping. The operator does not select an outcome.

This study ends at a terminal retrospective disposition. It cannot register Shadow or alter
v004/S004. A promotion attempt requires a separately initialized successor with exact `revisits`
lineage and later unused `verified-clean` evidence.

## Metrics and outcome rules

The fourteen shared screen gates are conjunctive:

1. completed trades are at least 20;
2. traded folds are at least three;
3. positive traded-fold ratio is at least 60%;
4. chained base compounded return is greater than zero;
5. chained base profit factor is greater than 1.1;
6. chained stress compounded return is greater than zero;
7. chained stress profit factor is greater than 1.0;
8. stress maximum drawdown is at most 20%;
9. no fold contributes more than 50% of completed trades;
10. no fold contributes more than 50% of total positive profit;
11. candidate base return exceeds cash;
12. candidate base daily-equity Sharpe exceeds baseline by at least 0.10;
13. candidate base return exceeds the 90th percentile exposure-matched random return; and
14. complete-family block-bootstrap selection confidence is at least 90%.

Additional study-specific constraints are also conjunctive: candidate base return is at least 90%
of baseline; candidate stress drawdown is no worse than baseline; each ATR boundary is binding on
at least two otherwise-eligible decisions across at least two folds; and the complete ATR band is
binding on at least five baseline-eligible decisions across at least three folds.

For `parameter-perturbation`, `delayed-entry`, `higher-costs`, `worse-fills`, `missed-entries`, and
`market-regimes`, the distinct artifact must expose all relevant raw metrics. Its frozen composite
gate is true only when every applicable numeric condition above remains satisfied; the reviewer
recomputes that conjunction from the artifact.

Terminal interpretation is fixed:

- `pass` plus `retrospectively-supported`: every required identity and gate is complete and
  passing; no promotion authority follows.
- `fail` plus `development-selection-failed`: complete trustworthy Development evidence finds no
  eligible candidate, with no candidate freeze, plan, or screen and with exact registry-absence
  proof.
- `fail` plus `retrospective-screen-failed`: the complete canonical screen contains at least one
  failed frozen gate.
- `indeterminate`: identity, classification, approval, family, artifact, registry replay, or other
  integrity evidence is missing or untrustworthy; `decision_stage` must identify the failing stage.
- `insufficient-evidence`: prohibited for this fixed completed-data checkpoint.

## Deviations and stopping rules

No outcome-relevant deviation is silently permitted. Stop and record the issue if any required
source, policy, manifest, observation, calendar, approval, registry event, challenge artifact, or
digest is missing, stale, conflicting, or non-replayable.

After preregistration, never change the hypothesis, route, calendar, family, parameters, baseline,
costs, metrics, thresholds, seeds, challenge targets, evidence classification, or outcome mapping.
Never use 2021-2025 outcomes to tune or replace the candidate. Never hide trials, produce partial
ranking, use mutable `latest` evidence, call a broker, create orders, or claim live authority.

Pause only through the guarded lifecycle with a concrete reason. If the frozen design itself must
change, cancel this study and initialize the next CLI-allocated successor with exact `revisits`.
Terminate the round after a governed Development no-candidate result, a complete retrospective
screen, irrecoverable evidence failure, trial-budget exhaustion, or explicit human stop.
