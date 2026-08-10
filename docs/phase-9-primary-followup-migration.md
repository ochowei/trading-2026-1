# Phase 9 primary-only followup migration

Updated 2026-08-10. The Phase 9 migration and representative-evidence stage is
closed at its fail-closed qualification boundary. This note does not claim that
any strategy is qualified, registered as Shadow, or cut over.

This file is the canonical current Phase 9 status, evidence ledger, and
parity/requalification/Shadow runbook. The
[Phase 9 pre-implementation report](superpowers/plans/2026-08-06-phase-9-pre-implementation-report.md)
remains a historical design baseline and is not updated retroactively with
execution status.

## Canonical current status and closure record

### Current position

The primary-only migration boundary and zero-bypass policy are implemented.
The source and evidence checkpoints are:

```text
branch: codex/experiment-data-access-migration-phase-9
source migration: 306fe1cdb2e07d8bb614872f82ae2d5fe942c838
source message: phase9: complete primary followup bundle migration
SPY evidence: c09e92be4ce68b02c1b93f8f37239a6e8a21b94f
evidence message: phase9: checkpoint SPY parity and formal observation
SPY evaluation preparation: e858cb1406b8d08b3d9c2887e92f00c9e6b2203f
preparation message: phase9: prepare complete SPY formal evaluation
```

The migration record covers 285 primary-only experiment entries, 571 primary
contract test cases, and 1226 tests in the full repository regression. The
intentional execution-model exceptions are the CIBR-014/SPY-007 tracer
implementations and nine TQQQ variants outside the primary followup contract.

SPY-007 reached the requalification gate; the other requested representatives
remain evidence-only or were not selected for new snapshot acquisition.
Requalification is not registered:

- Six migration-mode observations now exist; all remain `migration-pending`.
- The SPY asset-wide batch added nine valid `online` observations. SPY-007 also
  retains its earlier separate valid `offline` observation.
- No qualification registry, lifecycle registry, manual ledger, or
  reconciliation record is currently registered for this stage.
- No Shadow registration or global no-new-entry transition has been performed.
- No active promotion, broker order, or new entry has been performed.

The source checkpoint includes the original four migration observations. The
SPY evidence checkpoint adds one current-definition snapshot, one valid offline
result, one exact parity envelope, one linked migration result, and the two
append-only trial observations. Qualification and lifecycle state remain absent.

The later approved SPY asset-wide formalization published one current-definition
snapshot and one valid online observation for every registered SPY experiment.
That batch replaced the nine legacy `latest.json` files by design, but did not
change `followup.py`, qualification, lifecycle, ledger, reconciliation, or
broker state. The complete-set ranking retained SPY-007 as the formal followup
candidate under the repository evaluation workflow; its new snapshot also has
exact migration parity. This newer evidence resolves the former `legacy`
result-validity blocker, but it does not repair the pre-registration or
incomplete-selection-history blockers described below.

Phase 9 is therefore complete at the migration/evidence boundary. Its requested
requalification-to-Shadow continuation stopped at the mandatory historical-plan
guardrail. That stop is the correct terminal result for this phase, not an
authorization to weaken or backdate the Phase 6 qualification contract.

### Gate 3 attempt — SPY-007 formal observation blocked

The documented separate formal offline observation was attempted against the
existing SPY-007 snapshot. The runner correctly rejected it because the exact
definition blob reference changed even though the semantic fingerprint did not:

| Identity | Snapshot-bound definition | Current source definition |
| --- | --- | --- |
| Fingerprint | `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612` | `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612` |
| Blob digest | `02c227ad3e9bad06456d6013c9fd0c4e04a507108336aadfd499694790a15a4d` | `a7ccb179cad2918749e0b51898831bc2bd0e6840f0c487484ab8bfe2eb9cb53a` |
| Blob byte count | `113175` | `104792` |

The formal runner requires the exact definition reference to match the
snapshot; a matching semantic fingerprint alone is insufficient. The failed
attempt did not write a result, registry observation, `latest.json`,
qualification state, or lifecycle state. The existing snapshot was not
overwritten or rebound, and the migration result was not treated as a formal
observation. The later approved publication used an explicit 2026-08-06
decision cutoff and created a new immutable snapshot.

### Gate 3 completion — SPY-007

After the approved full refresh, a new immutable snapshot was published and
verified:

- snapshot: `fca6ea038930468a383b3f9c598700e8ed5ce9923a2f772536eeb227f4e04778`;
- decision session: `2026-08-06`;
- current definition digest: `a7ccb179cad2918749e0b51898831bc2bd0e6840f0c487484ab8bfe2eb9cb53a`;
- semantic definition fingerprint: `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612`.

The separate formal offline observation then succeeded at
`results/spy_007_trend_pullback/20260807_063639_341769_offline_640017db49b749408ec9e3a855c2acb1.json`
with registry observation ID `6e378591fc5943cd90ffa9c6182c8866` and
`validity_status=valid`. It did not update `latest.json`.

The new snapshot's provider-free migration parity also passed exactly. Its
immutable artifact is
`results/spy_007_trend_pullback/fca6ea038930468a383b3f9c598700e8ed5ce9923a2f772536eeb227f4e04778.migration-parity.json`
with parity digest
`c7cee27475aa2da97efd16b6039e0b64e56355c8f8169c81ca9b3e0eada0e5e1` and no
differences. The linked migration result remains `migration-pending` and is
not the qualification observation. All four current-definition artifacts and
their trial observations are checkpointed in commit
`c09e92be4ce68b02c1b93f8f37239a6e8a21b94f`.

### Gate 4 blocked — frozen historical plan is not registered

The read-only checks after the SPY-007 observation report:

- `trading qualification status`: qualification registry is empty;
- `trading followup-state status`: lifecycle registry is not initialized;
- no manual ledger or broker reconciliation record exists.

At this closure checkpoint the codebase exposed Python APIs for a frozen
`HistoricalQualificationPlan` and `HistoricalScreenResult`, but no production
CLI constructed and registered the plan/screen sequence. The later
`qualification plan register` and `qualification screen run` commands now
provide that boundary through a forward-only selection epoch; they do not
retroactively change this closure result or permit these already observed
sessions to qualify. A safe requalification requires an explicit plan covering development years,
evaluation folds, family trial inventory (including legacy variants), benchmark
and random-selection policy, cost scenarios, and exact cutoff/session rules.
Those inputs cannot be inferred from migration parity or the one valid offline
observation. No qualification or lifecycle state is created until that plan
and its operator-approved execution procedure exist. Operator confirmation on
2026-08-07 established that no repository-external pre-registered plan or event
is available for SPY-007. Historical requalification is therefore blocked
under the current contract; no dates or plan timestamp may be backdated.

### Disposition — preserve the pre-registration guardrail

The approved disposition is to retain the existing historical-plan contract and
record SPY-007 as `requalification-blocked`. No one-time backdated exception,
qualification event, Shadow registration, or lifecycle transition will be
created. Any future qualification effort must begin with a newly frozen,
forward-dated plan and an explicitly approved observation schedule; it cannot
reuse this migration evidence as a substitute for plan registration.

That future work is a new prospective Phase 6/7 qualification program. It is
not unfinished Phase 9 migration work and cannot make SPY-007 immediately
Shadow-eligible.

### Post-closure prospective-program preflight

The operator approved starting a new forward-dated qualification program on
2026-08-07. The read-only preflight stopped before plan registration because
the evidence at that checkpoint could not satisfy the frozen Phase 6 inputs.
The 2026-08-10 follow-up implemented and formally observed the missing
comparator, while still stopping before any epoch or plan registration:

- At the 2026-08-07 checkpoint, `trading result status
  spy_007_trend_pullback` reported `legacy`; the separate valid offline
  observation was immutable historical evidence and did not replace
  `latest.json`. By the 2026-08-10 review, the persisted result was
  `data-stale`. Neither status can serve as a future epoch observation.
- The verified trial registry has `selection_history_incomplete=true`. At this
  checkpoint the family-wise selection-adjustment contract rejected that global
  state before evaluating any family returns. The later Forward Selection Epoch
  boundary preserves the flag and can use only preregistered future sessions.
- At preflight, `SPY:trend-pullback` contained one complete semantic trial and
  no separately verified family-baseline trial covering future frozen evaluation
  sessions. SPY-010 now freezes the documented SPY-007 Attempt 2 definition and
  has a valid schema-3 online observation through 2026-08-07 as trial
  `a960a0c24a544e063ca3e97b9c29933f7dde2b58ac50356eb2672905c658eaf3`.
- The SPY experiment overview records all three SPY-007 attempts as failed with
  structurally weak Part A performance and names SPY-009 as the historical best.
  SPY-009's persisted result is also currently `data-stale`, so it cannot be
  silently substituted as a qualified candidate or baseline.

No `HistoricalQualificationPlan` or Forward Selection Epoch was registered.
The formal family universe is now SPY-007 selected trial plus the distinct
SPY-010 baseline trial. The remaining prerequisite is an operator-approved
future observation schedule; only then may a forward-dated plan freeze the exact
trial manifests and included trial identities. Replacing SPY-007 with a new
candidate/family or ending its followup candidacy remain separate research-scope
choices and are not inferred from the Phase 9 migration approval.

### Approved SPY asset-wide formal-evaluation preparation

At that checkpoint, the operator approved preparing the complete SPY candidate
set but did not authorize an external download or a `latest.json` rewrite. The
later SPY-010 comparator run was separately authorized on 2026-08-10 and does
not alter this dated nine-candidate ranking evidence. The candidate inventory
was fixed at all nine registered SPY experiments; no legacy metric was used to
omit or rank a candidate:

| Candidate | Trial family | Declared data | Current definition fingerprint | Persisted status |
| --- | --- | --- | --- | --- |
| SPY-001 `spy_001_pullback_wr` | `SPY:pullback-wr` | SPY primary from 2010-01-01 | `427dcafd26bee97eba0e5a06e90288d0e27591252bc21cf5d19d5f616148b919` | `legacy` |
| SPY-002 `spy_002_no_trailing` | `SPY:no-trailing` | SPY primary from 2010-01-01 | `980da6a7dc8796e85f6340ad80e71e6eef2989d1c4fc74f9df13d7b043feaaac` | `legacy` |
| SPY-003 `spy_003_optimized_wr` | `SPY:vix-filter` | SPY primary and `^VIX` auxiliary from 2010-01-01 | `b5252d106f40eb4b7054768f469470d06231a4131ba6b0f9c886c4d2693cda59` | `legacy` |
| SPY-004 `spy_004_rsi2_reversal` | `SPY:rsi2-reversal` | SPY primary from 2010-01-01 | `abb0b16c78fc85cf15bf5a8e78505501391a80390a6a965f388f86e4f062921f` | `legacy` |
| SPY-005 `spy_005_asymmetric_exit` | `SPY:asymmetric-exit` | SPY primary from 2010-01-01 | `56c4876acc9da8cd60053bc4dbbbf848785b6142767037c786fe2f51de370d81` | `legacy` |
| SPY-006 `spy_006_roc_reversal` | `SPY:roc-reversal` | SPY primary from 2010-01-01 | `36cc682c5019231234517f3365326b23fc98dcbf2e820b531623f60e1c5974c4` | `legacy` |
| SPY-007 `spy_007_trend_pullback` | `SPY:trend-pullback` | SPY primary from 2010-01-01 | `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612` | `legacy` latest; separate offline observation `valid` |
| SPY-008 `spy_008_bb_squeeze_breakout` | `SPY:bb-squeeze-breakout` | SPY primary from 2018-01-01 | `8d71ee42db60a8316b00b131def2e776cd765dc779eda712d600288b3e1bf2d0` | `legacy` |
| SPY-009 `spy_009_capitulation_filter` | `SPY:capitulation-filter` | SPY primary from 2010-01-01 | `80128513b79dd9ec5b3dc1a57615f9b8f37248cbd4cf3e730b97c1f1a6924391` | `legacy` |

All nine are snapshot-aware `ExecutionModelStrategy` implementations. The
latest completed XNYS session at the preflight clock is 2026-08-06. The SPY
cache is valid through that session and records a complete refresh at
2026-08-07T06:36:10.796943Z with data digest
`25ec8f1259440551ad520717ecf8a63bb7517d35b37cb313a9ab8e05a74cdc56`.
The `^VIX` cache required only by SPY-003 is missing. Therefore the proposed
decision cutoff is explicitly 2026-08-06; it is derived from both the calendar
and verified primary cache, not guessed.

The formalization batch must use one consistent source state and cutoff:

1. Obtain explicit approval for one full `^VIX` refresh through 2026-08-06.
2. Re-verify SPY and `^VIX`, then publish nine new immutable manifests using
   the current exact definition references. Reuse the one verified SPY blob;
   do not issue nine redundant provider downloads. SPY-003 alone includes the
   aligned `^VIX` auxiliary blob and its declared one-session publication lag.
3. Verify every manifest before execution. The existing SPY-007 manifests are
   retained as evidence but are not reused because their exact captured
   definition references belong to earlier source checkpoints.
4. Run each candidate once with `trading run <experiment> --snapshot
   <manifest>`. This is formal `online` mode: it intentionally advances that
   candidate's `latest.json`, writes one immutable historical result, and
   appends one valid observation to `results/trial_registry.json`.
5. Re-run result status for all nine. If any candidate is not exactly `valid`,
   stop without ranking and without changing followup selection.
6. Only after the complete set is valid, compare all nine, run gradient
   analysis on the best candidate, and produce the followup qualification
   checklist. The historical SPY-009 result is a hypothesis, not a ranking
   input.
7. Keep the ranking decision separate from evidence publication. Do not edit
   `followup.py`, qualification state, lifecycle state, ledger state, or broker
   state in the formalization batch.
8. If a new candidate is selected, generate exact fixed-snapshot migration
   parity for that selected definition before any later qualification handoff.

`trading result evaluate SPY` is not the preparation command for this batch:
the current implementation refreshes only stale schema-3 candidates and will
fail closed on these nine legacy results. Snapshot preparation and formal runs
must therefore be explicit and fully reviewed.

The next state-changing gate requires one combined operator approval: download
`^VIX` through the 2026-08-06 cutoff, publish the nine immutable manifests, and
allow the nine formal `--snapshot` runs to replace their legacy `latest.json`
files. This approval still does not authorize Shadow or Active promotion.

### SPY asset-wide formal-evaluation completion

The operator granted the combined approval. The batch completed on 2026-08-07
against one source state and the explicit 2026-08-06 decision session.

The SPY cache remained valid through the cutoff. The first generic `^VIX`
refresh attempt correctly stopped on a coverage-policy mismatch because the
standalone data CLI assumes XNYS sessions. The retry used SPY-003's declared
`provider_observations` coverage policy, completed a full 9,217-row refresh
through 2026-08-06, and passed exact snapshot verification. No cutoff or
missing observation was guessed. The generic standalone `data status ^VIX`
command still cannot infer an experiment-specific coverage policy; the
SPY-003 manifest verification is the authoritative check for this batch.

All manifests below passed `trading data verify`. Each formal online run wrote
one schema-3 `valid` observation and intentionally replaced that experiment's
legacy `latest.json`. All nine latest results report data cutoff 2026-08-06 and
the exact fingerprint shown here.

| Candidate | Snapshot ID | Definition fingerprint | Valid observation ID |
| --- | --- | --- | --- |
| SPY-001 | `66bd5c33c6810d8dd139be2c56b212d831aefad9ad544049ac48e80dd6d9bfa2` | `427dcafd26bee97eba0e5a06e90288d0e27591252bc21cf5d19d5f616148b919` | `0d8528436788493ba8e5de6eebdee796` |
| SPY-002 | `48a6e0aaca76a4dffbc27ea0de8fcea2b1a9726532021f3130751c2286c5ff8f` | `980da6a7dc8796e85f6340ad80e71e6eef2989d1c4fc74f9df13d7b043feaaac` | `48e848e48ebc42229a998ced19d9804c` |
| SPY-003 | `822bb1741f4e96795805d12a42a042a3c85114bacb3e0c93e93fee7816f05c4a` | `b5252d106f40eb4b7054768f469470d06231a4131ba6b0f9c886c4d2693cda59` | `1127b8b8db334e119117a79ca1fb0ef2` |
| SPY-004 | `2abb1415a9b27ce0f0d4ae8493f0eabeb378ef4721abf7035532c92cf3a81859` | `abb0b16c78fc85cf15bf5a8e78505501391a80390a6a965f388f86e4f062921f` | `2fa9a07ae73b485abc813b8773845350` |
| SPY-005 | `91ce89af4a997c61c573004bb86726bb6c893594c20e559fb4fa7aa90cbe31d5` | `56c4876acc9da8cd60053bc4dbbbf848785b6142767037c786fe2f51de370d81` | `59dbb1b02b074d1da5041323d679d893` |
| SPY-006 | `f3c3041632b70bdbb2c42f47cd195827456bdbc9a1ed8d995eb7d8554f96033e` | `36cc682c5019231234517f3365326b23fc98dcbf2e820b531623f60e1c5974c4` | `51f094a252f4495e99096860d6779190` |
| SPY-007 | `2e698ed59c223049b3bc3f8297092b6eca6b91710358e499e298f2c4357cd1e8` | `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612` | `3cb1d36e52814bebb38622d7f7deb30e` |
| SPY-008 | `925023588ed1cce85b63fc82306f34746165dab052c56e15b2f366eff5d93347` | `8d71ee42db60a8316b00b131def2e776cd765dc779eda712d600288b3e1bf2d0` | `2e743c229f7840878b69742dcf33628b` |
| SPY-009 | `44d839a58acef398fbf6581b435905931960c801a24354a8a42d7934c76d6cf3` | `80128513b79dd9ec5b3dc1a57615f9b8f37248cbd4cf3e730b97c1f1a6924391` | `1eb3ad995d604a1dacbb903a6abbe9eb` |

The complete valid-set comparison, using the repository's formal followup
ranking priorities, is:

| Rank | Candidate | Part B WR | Part B cumulative | Part B Sharpe | A/B WR difference | Ranking eligibility |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | SPY-007 | 68.75% | +18.35% | 0.42 | 11.61pp | Yes |
| 2 | SPY-008 | 75.00% | +9.85% | 0.34 | 4.41pp | Yes |
| 3 | SPY-009 | 100.00% | +9.27% | 0.00 | 0.00pp | Yes |
| 4 | SPY-006 | 75.00% | +7.43% | 0.65 | 6.25pp | Yes |
| 5 | SPY-005 | 75.00% | +5.89% | 0.56 | 0.00pp | Yes |
| 6 | SPY-004 | 75.00% | +4.89% | 0.55 | 12.50pp | Yes |
| — | SPY-002 | 75.00% | +4.89% | 0.55 | 15.00pp | No: consistency requires less than 15pp |
| — | SPY-003 | 100.00% | +13.14% | 0.00 | 50.00pp | No: A/B inconsistency |
| — | SPY-001 | 75.00% | -1.41% | -0.15 | 5.00pp | No: Part B cumulative return is not positive |

This ranking does not rewrite the historical experiment-design conclusion that
SPY-009 has the highest legacy min(A,B) Sharpe convention. It answers a
different question: the formal followup workflow ranks eligible candidates by
Part B cumulative return after its mandatory validity and consistency gates.
Under that policy SPY-007 ranks first, and it was already the configured SPY
followup entry, so `src/trading/followup.py` did not change.

The SPY-007 followup checklist passes the repository's generic research
candidate thresholds: result `valid`; Part B WR 68.75%; Part B cumulative
+18.35%; 16 signals over two years, or 8.0/year; A/B WR difference 11.61pp;
`ExecutionModelStrategy`; and downstream cumulative-return evolution gradual
despite abrupt rolling win-rate changes. Its 2026 Part C result is negative
(-5.48%) and remains an explicit risk input for any future historical screen;
Part C is not one of the generic ranking gates and has not been hidden or
reclassified.

SPY-007's selected current snapshot was also replayed through both the legacy
DataFetcher path bound to the verified bundle and the provider-free bundle
path. Indicators, ordered signal dates, and filled trades matched exactly.
The immutable parity digest is
`3a0be6b8eaa37d373fbc3dc19acdd9b30a2510af5925be5bad7ea19811b033ff`.
The linked migration observation ID is
`9c64a4b4ea4a45bda74d3c2559febfff`; it remains `migration-pending` and did
not modify SPY-007 `latest.json`.

This completes the approved asset-wide evidence batch. It does **not** create
formal Phase 6 qualification: `selection_history_incomplete` remains true,
there is no pre-registered historical plan for these already-observed sessions,
the qualification registry is empty, and the lifecycle registry is not
initialized. No Shadow/no-new-entry state or Active promotion was created.
Any next qualification attempt is a new forward-dated Phase 6/7 program with
future observation sessions, not remaining Phase 9 implementation.

### Existing immutable evidence

The following artifacts are present under `results/` and passed the exact
indicator, ordered signal-date, and filled-trade comparison. The migrated
definition fingerprint is the `result_fingerprint` in the parity envelope.

| Experiment | Current followup scope | Snapshot ID | Definition fingerprint | Parity digest | State |
| --- | --- | --- | --- | --- | --- |
| `spy_007_trend_pullback` (SPY-007), asset-wide formal selection | Yes | `2e698ed59c223049b3bc3f8297092b6eca6b91710358e499e298f2c4357cd1e8` | `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612` | `3a0be6b8eaa37d373fbc3dc19acdd9b30a2510af5925be5bad7ea19811b033ff` | Parity `migration-pending`; separate online observation `valid`; requalification blocked |
| `spy_007_trend_pullback` (SPY-007), current | Yes | `fca6ea038930468a383b3f9c598700e8ed5ce9923a2f772536eeb227f4e04778` | `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612` | `c7cee27475aa2da97efd16b6039e0b64e56355c8f8169c81ca9b3e0eada0e5e1` | Parity `migration-pending`; separate offline observation `valid`; requalification blocked |
| `spy_007_trend_pullback` (SPY-007), historical parity | Yes | `ca54bc84ab26762438567d820257941c1ba00b42a8a833a4de9226a13db85111` | `f75526cd9b8493f26a250d1db915c8c57176bb59e941332bee95bc0870d66612` | `89be61317ff48bc298d33083fd012ec74b56c2afe90cf6119f010214ab70c62b` | Retained immutable migration evidence |
| `sivr_001_mean_reversion` (SIVR-001) | No | `2f4b8260a913919a7785e961dba772d7aa7f226f3689bce07cbf079314e7b5d4` | `228e219cdbbbabc4e84d8561139a963b1501d5680378c8bdef02692147667259` | `d01501158c2dcfb2f0b25276b0be78dc3986f9b4c84daeb5300176ab1564eb18` | `migration-pending` |
| `tsla_001_extreme_oversold` (TSLA-001) | No | `5a7f48e9e134b1cbe16c492446d47653bcdb84e100676775c2dec3051ec1a9e7` | `d951579fd99a92b519ff4edbb96903877c74a500fb29f2dfda7d1b63dd789945` | `ecbe0eb4f0d6f3624dad10e1d4215af035b8438c448c35a73cdc2101f4a4f389` | `migration-pending` |
| `voo_001_rsi2_reversal` (VOO-001) | No | `ea33ffb51e318408675549b451d97c6eff9718965a813aa1db0c663714f3637c` | `8368f3c1224980eb10712aeac7a0151d4b2b09ce0a6352966eb2809cde69b8b0` | `438deb343b6522d4d5b2be866015cec06d17079d7a2f4e69c9b1110745718c44` | `migration-pending` |

The parity artifacts do not replace `latest.json`, do not qualify a trial, and
do not establish a lifecycle transition.

### Requested representative scope

The requested representative list is larger than the current followup strategy
list. Evidence for a non-followup experiment must not silently expand followup
scope.

| Representative | Current followup entry | Snapshot inventory | Current decision |
| --- | --- | --- | --- |
| SPY-007 | Yes | New current-definition snapshot published | Parity and valid observation passed; `requalification-blocked` because no pre-registered historical plan exists |
| SIVR-001 | No | Existing immutable snapshot | Keep as migration evidence unless scope is explicitly changed |
| TSLA-001 | No | Existing immutable snapshot | Keep as migration evidence unless scope is explicitly changed |
| VOO-001 | No | Existing immutable snapshot | Keep as migration evidence unless scope is explicitly changed |
| EEM-021 (`eem_021_bb_width_regime_gate_mr`) | No | No matching snapshot found | Do not guess cutoff; create only after freshness/cutoff approval |
| NVDA-013 (`nvda_013_regime_mbpc`) | No | No matching snapshot found | Do not guess cutoff; create only after freshness/cutoff approval |
| USO-009 (`uso_009_momentum_pullback`) | Yes | No matching snapshot found | Not selected for this closure; any future evidence requires a separately approved cutoff |
| XBI-015 (`xbi_015_regime_pullback_mr`) | No | No matching snapshot found | Do not guess cutoff; create only after freshness/cutoff approval |

If a missing snapshot requires external data download or a human-selected
decision date, execution pauses at this gate. Existing snapshots must never be
overwritten.

### State and evidence invariants

1. Migration parity is an equivalence check, not qualification evidence.
2. A migration-mode observation cannot satisfy
   `ExperimentTrialRegistry.has_valid_observation()`.
3. A separate successful formal `online` or `offline` observation with current
   definition identity, trial identity, and freshness is required before
   historical requalification or Shadow registration.
4. Migration runs must not rewrite `latest.json`, qualification state, or
   lifecycle state.
5. Parity failure stops that strategy; no tolerance is widened and no evidence
   is overwritten.
6. Shadow registration is not active promotion. No broker order or new entry is
   permitted in this stage.
7. Global no-new-entry initialization requires an actual manual ledger and
   broker reconciliation; it must not be manufactured from absent state.

### Gated execution plan

#### Gate 0 — registry/worktree checkpoint

- Confirm the source worktree and branch are the intended Phase 9 checkpoint.
- Preserve the SPY artifacts and append-only registry observations in evidence
  checkpoint `c09e92be4ce68b02c1b93f8f37239a6e8a21b94f`.
- Keep ignored caches, locks, and private state out of source/evidence commits.
- Do not start a state-changing workflow while registry ownership is ambiguous.

#### Gate 1 — representative scope and snapshot

- Freeze which representatives are evidence-only and which are current followup
  candidates.
- Reuse the four existing immutable snapshots where applicable.
- For EEM-021, NVDA-013, USO-009, and XBI-015, verify whether an exact
  immutable snapshot exists; if not, obtain an approved data cutoff and
  freshness decision before creating one.
- Verify snapshot manifests, data blobs, definition identity, and auxiliary
  coverage without changing existing artifacts.

#### Gate 2 — migration parity

For each selected snapshot, run the documented offline migration workflow:

```text
uv run trading run <experiment_name> --offline \
  results/<experiment>/<snapshot_id>.snapshot.json \
  --migration-parity results/<experiment>/<snapshot_id>.migration-parity.json
```

Review the immutable envelope for indicators, ordered signal dates, filled
trades, legacy and migrated definition identities, layer checksums, parity
digest, an empty difference summary, and passing status. The result must remain
`migration-pending`; do not update `latest.json` or any qualification/lifecycle
state. The CLI consumes an existing parity artifact; it does not generate one.
Artifact generation must use the existing verified parity domain API and write
only after an exact pass, or a bounded equivalent workflow must be documented
before another strategy is processed.

#### Gate 3 — separate valid formal observation

Only a parity-passing strategy that is in current followup scope may proceed.
Create a separate formal `online` or `offline` observation using the current
definition and trial identity. Verify registry validity, freshness, result
fingerprint, and snapshot identity. The migration result itself cannot be
reused as this observation.

SPY-007 completed this handoff through the formal offline runner; the result was
not copied or promoted into `latest.json`. Any later strategy must repeat the
same verified snapshot, current-definition, and formal-run procedure.

#### Gate 4 — historical requalification

For each strategy with a separate valid observation:

- freeze the historical plan and definition identity;
- verify complete trial/family history, including legacy variants and any
  `selection_history_incomplete` constraints;
- run the historical screen and benchmark/family-wise selection checks;
- record the historical screen and selection events append-only;
- leave any failing, stale, or incomplete strategy unqualified.

No qualification state may be created merely because migration parity passed.
For this closure, Gate 4 is blocked because the required plan was not registered
before the first evaluation outcome. Do not execute or backdate a screen.

#### Gate 5 — Shadow registration

Only after Gate 4 passes, register per-strategy Shadow with the exact selected
trial, result fingerprint, definition snapshot, parity digest, historical screen
event, registration event, prospective start, and activation checkpoint.

Keep global no-new-entry enabled. `followup-state shadow` is not a substitute
for the required historical screen or formal observation.

#### Gate 6 — prospective Shadow evidence (later)

Collect paper/non-actionable evidence under the Phase 6/7 rules, including the
required session and paper-fill counts, base/stress performance gates, and
drift checks. Activation remains a later, separately approved phase and is not
part of this checklist.

### Human approval points

The following require explicit operator confirmation before state-changing work:

- whether SIVR-001, TSLA-001, VOO-001, EEM-021, NVDA-013, or XBI-015 should remain
  evidence-only or be added to followup scope;
- any external data download, data cutoff, or snapshot freshness exception;
- registration of a new forward-dated Historical Qualification Plan and its
  observation schedule;
- manual ledger initialization and broker reconciliation before a global
  no-new-entry state is established;
- any future activation or promotion request.

### Items not explicit in the Phase 9 source documents

These operational details are inherited partly from the Phase 6/7 documents or
are deliberately deferred outside this Phase 9 closure:

1. A representative-to-followup scope matrix and its change-approval rule.
2. A per-strategy snapshot acquisition, cutoff, and freshness runbook.
3. The concrete formal-observation handoff from migration evidence.
4. Treatment of incomplete legacy selection history in family-wise
   requalification.
5. Ownership of manual ledger, reconciliation, and global no-new-entry state.
6. Shadow observation schedule, session clock, paper-fill source, and stopping
   criteria.
7. Retention/checkpoint rules for immutable evidence versus mutable registries.
8. Final compatibility cleanup: adapter removal, legacy CLI execution policy,
   authoring skill/workflow updates, and the remaining out-of-scope TQQQ audit.

### Closure checklist

| Check | Status | Evidence or disposition |
| --- | --- | --- |
| Architecture and zero-bypass policy | Complete | 285 primary-only entries, empty active allowlist, provider boundary clean |
| Complete SPY formal set | Complete | Nine current-definition snapshots and nine valid online observations at decision session 2026-08-06 |
| Selected representative snapshot | Complete | SPY-007 snapshot `2e698ed59c223049b3bc3f8297092b6eca6b91710358e499e298f2c4357cd1e8` |
| Exact parity | Complete | Digest `3a0be6b8eaa37d373fbc3dc19acdd9b30a2510af5925be5bad7ea19811b033ff`; no differences |
| Separate formal observation | Complete | SPY-007 online observation `valid` and distinct from migration result |
| Historical requalification | Blocked | No plan pre-registered before the first evaluation outcome; no backdating |
| Shadow registration | Not reached | Qualification registry empty; lifecycle registry not initialized |
| Global no-new-entry | Fail-closed, not initialized | Missing lifecycle state authorizes no new entry; no fabricated ledger/reconciliation |
| Result/state protection | Complete | Nine legacy latest results were intentionally formalized under explicit approval; qualification, lifecycle, ledger, reconciliation, and broker state did not change |
| Active promotion | Not performed | No broker order or new entry occurred |

Closure classification: **Phase 9 migration complete; requalification blocked;
Shadow/no-new-entry state not initialized; active promotion prohibited.**

The asset-wide formalization resolved the former SPY result-validity blocker
but did not change this classification: no plan was registered because complete
selection history and a prospective historical-screen plan remain unresolved.

The migrated strategies declare one adjusted-daily primary series through
`market_data_requirements()`, capture an immutable research definition and
trial family, and execute only through a verified `MarketDataBundle`. Their
`run_with_bundle()` output includes the typed canonical sleeve input required
by formal offline runs. `run_for_parity()` exposes ordered indicators, signal
dates, and filled trades for fixed-snapshot migration evidence.

The shared implementation is
`src/trading/core/bundle_strategy.py`. It is deliberately provider-free and
captures its own source in each definition fingerprint. The CIBR-014 and
SPY-007 strategies retain explicit implementations because they are the
tracer slices; the other primary-only followup strategies use the shared mixin.

Migrated primary-only followup strategies:

- CIBR-014, SPY-007
- COPX-007, DIA-013, EEM-012, EWJ-002, EWT-001, EWZ-006
- FCX-008, FXI-005, INDA-010, IWM-006, SIVR-006, SOXL-005
- TSM-006, URA-003, USO-009, VGK-007, VOO-003, XLU-002

The contract tests use synthetic verified bundles and assert that provider
access is not needed. Each shared-mixin strategy also completes a formal
offline schema-3 execution in a temporary result root. These tests do not
write repository `results/`, advance `latest.json`, or change qualification
and lifecycle state. A migration-mode result remains `migration-pending` and
requires a later separate valid formal observation before followup activation.

The historical auxiliary alignment contract is now implemented in
`ResearchDataStore` and `MarketDataBundle`: snapshot replay supplies one
ordered decision sequence, and every auxiliary observation is aligned
backward to each primary decision under an explicit one-session publication
lag and provider-observation coverage policy. The contract fails closed when
the first decision cannot be satisfied. The following six auxiliary
strategies now use the shared `AuxiliaryBundleStrategyMixin` and complete the
same provider-free formal offline contract tests:

- GLD-016 (`GLD:dxy-divergence-mr`)
- NVDA-007 (`NVDA:rs-exit-optimized`)
- TLT-017 (`TLT:yield-curve-slope-mr`)
- TQQQ-025 (`TQQQ:vxn-vix-vvix-filter`)
- TSLA-017 (`TSLA:qqq-divergence-breakout`)
- XBI-018 (`XBI:xbi-xlv-divergence-mr`)

These migration runs remain `migration-pending`; no latest result or
followup qualification is created until a separate valid formal observation
is recorded.

## SPY-007 fixed-snapshot evidence

On 2026-08-07, SPY-007 was replayed against the immutable snapshot
`ca54bc84ab26762438567d820257941c1ba00b42a8a833a4de9226a13db85111`, covering
the declared SPY primary series from 2010-01-01 through the 2026-08-06
decision session. The legacy DataFetcher path was bound to the exact snapshot
frame and compared with `run_for_parity()`; indicator, signal-date, and filled-
trade layers matched exactly. The passing parity digest is
`89be61317ff48bc298d33083fd012ec74b56c2afe90cf6119f010214ab70c62b`.

The result-linked artifacts are the snapshot manifest,
`results/spy_007_trend_pullback/<snapshot_id>.snapshot.json`, the local parity
evidence, and the migration result. The migration result is schema 3,
`migration-pending`, requires requalification, and does not replace
`results/spy_007_trend_pullback/latest.json` or alter qualification/lifecycle
state.

The first asset-wave tracer replays also passed. SIVR-001 used snapshot
`2f4b8260a913919a7785e961dba772d7aa7f226f3689bce07cbf079314e7b5d4` with
parity digest `d01501158c2dcfb2f0b25276b0be78dc3986f9b4c84daeb5300176ab1564eb18`.
TSLA-001 used its declared 2018-01-01 history start with snapshot
`5a7f48e9e134b1cbe16c492446d47653bcdb84e100676775c2dec3051ec1a9e7` and parity
digest `ecbe0eb4f0d6f3624dad10e1d4215af035b8438c448c35a73cdc2101f4a4f389`.
Both matched indicators, signal dates, and filled trades exactly; both
migration results remain `migration-pending` and leave `latest.json` and
qualification state unchanged.

## PR4 first asset-sized slice

SPY-003 (`spy_003_optimized_wr`) is the first non-followup asset-sized
migration. Its detector now declares `^VIX` as one auxiliary provider-
observation series and consumes only the historical as-of frame supplied by
`AuxiliaryBundleStrategyMixin`; the direct yfinance bypass is removed. The
same provider-free bundle and formal offline tests cover this slice, and its
allowlist entry is removed after the scanner confirms the provider boundary.

URA-006 (`ura_006_trend_pullback`) is the second slice in the same commodity
wave. It declares XLE as one auxiliary provider-observation series, removes
the detector's direct yfinance fetch, and is covered by the same formal
offline contract. Its migration is also `migration-pending` and does not
advance latest or qualification state.

CIBR-006 (`cibr_006_rs_momentum_pullback`) is the third single-auxiliary
slice. It declares SPY as a provider-observation benchmark and removes the
legacy direct fetch while preserving the existing RS, ATR, and cooldown
logic behind the fail-closed bundle boundary.

TSM-007, TSM-008, TSM-011, TSM-012, TSM-016, TSM-017, TSM-018, TSM-019, and
TSM-022 are the semiconductor-pair slices. Each declares SMH plus any
volatility auxiliary series as provider-observation inputs and retains its
existing RS signal logic and execution-model differences while routing data
through the shared bundle boundary.

NVDA-006, NVDA-008, NVDA-014, and NVDA-015 are the next single-reference
asset slice. NVDA-006, NVDA-014, and NVDA-015 declare SMH; NVDA-008 declares
SPY. Their existing relative-strength, mean-reversion, and regime calculations
now consume only the aligned historical auxiliary frame supplied by the
verified bundle. The four migrations remain `migration-pending`; they do not
write latest results or create followup qualification.

The remaining TSM direct-fetch slices are now covered as one multi-auxiliary
wave: TSM-009 declares NVDA; TSM-013, TSM-014, and TSM-021 declare SMH plus
QQQ; TSM-015 declares SMH, AAPL, and QQQ; and TSM-020 declares SMH plus SOXX.
All six preserve their existing signal calculations while requiring the
verified as-of bundle, and remain `migration-pending` without latest or
qualification changes.

TSLA-018, TSLA-019, and TSLA-020 form the next three-strategy macro slice.
Each declares QQQ plus its DXY, VIX, or UUP auxiliary series and removes the
detector's provider access. The existing breakout and regime gates remain
unchanged behind the shared bundle boundary; these migrations also remain
`migration-pending`.

GLD-015 and GLD-017 are the next precious-metals slice. GLD-015 declares GVZ;
GLD-017 declares GVZ plus UUP. Both retain their existing capitulation,
volatility, and USD regime calculations while requiring aligned historical
auxiliary frames from the verified bundle, with migration-pending result
semantics.

FCX-006, FCX-015, and FCX-016 form the next asset-sized auxiliary slice.
FCX-006 declares COPX for relative-strength calculations; FCX-015 and FCX-016
declare ^VIX for their breakout regime gates. Their existing signal and
execution-model logic now consumes only the aligned historical auxiliary
frames supplied by the verified bundle. These migrations remain
migration-pending and do not advance latest results or followup qualification.

FXI-007, FXI-015, FXI-016, and FXI-017 form the China/currency auxiliary
wave. FXI-007 declares EEM; FXI-015 declares ASHR; FXI-016 declares ASHR and
CNY=X; and FXI-017 declares CNY=X. Their existing relative-strength,
divergence, and currency-regime calculations now consume only aligned
historical auxiliary frames from the verified bundle. These migrations remain
migration-pending and do not advance latest results or followup qualification.

EWT-007, EWT-010, EWT-011, and EWT-012 form the Taiwan/EM auxiliary slice.
Each declares EEM for its relative-strength or divergence calculations and
retains its existing momentum or mean-reversion execution model behind the
provider-free bundle boundary. SOXL-010 declares SOXX and SPY for its sector
relative-strength gate, while SOXL-011 declares SOXX for its ATR regime gate.
All six migrations remain migration-pending and do not advance latest results
or followup qualification.

CIBR-017, NVDA-018, NVDA-021, and VGK-009 complete the remaining direct
provider-bypass wave. CIBR-017 declares ^VIX; NVDA-018 declares ^VXN; NVDA-021
declares QQQ; and VGK-009 declares EURUSD=X. Their existing volatility,
divergence, and bilateral-FX calculations now consume only aligned historical
auxiliary frames from the verified bundle. All four migrations remain
migration-pending and do not advance latest results or followup qualification.

EEM-006, EEM-016, EEM-017, EEM-018, EEM-019, EEM-020, and EEM-022 are the
broad-emerging-markets auxiliary wave. They declare SPY, DXY, EFA, ^VIX, FXI,
or the relevant multi-anchor combination as provider-observation inputs and
keep their existing mean-reversion or relative-strength calculations behind
the fail-closed bundle boundary. These seven migrations remain
migration-pending and do not advance latest results or followup qualification.

INDA-007, INDA-012, INDA-013, INDA-014, and INDA-015 form the India auxiliary
wave. INDA-007, INDA-012, and INDA-013 declare EEM; INDA-014 declares DXY;
and INDA-015 declares ^MOVE. Their existing relative-strength, broad-EM,
currency-direction, and implied-volatility gates now consume only aligned
historical auxiliary frames from the verified bundle. All five migrations
remain migration-pending and do not advance latest results or followup
qualification.

EWZ-005, EWZ-008, EWZ-009, and EWZ-010 form the Brazil/EM auxiliary wave.
EWZ-005 and EWZ-009 declare EEM; EWZ-008 declares ^VIX; and EWZ-010 declares
both EEM and BRL=X. Their existing relative-strength, volatility, divergence,
and currency-regime calculations now consume only aligned historical
auxiliary frames from the verified bundle. All four migrations remain
migration-pending and do not advance latest results or followup qualification.

EWJ-004, EWJ-006, and EWJ-007 form the Japan auxiliary wave. EWJ-004 declares
SPY, EWJ-006 declares JPY=X, and EWJ-007 declares ^VIX. Their existing
relative-strength, currency-direction, and implied-volatility calculations now
consume only aligned historical auxiliary frames from the verified bundle. All
three migrations remain migration-pending and do not advance latest results or
followup qualification.

DIA-009, DIA-014, DIA-015, DIA-016, and DIA-018 form the broad-index auxiliary
wave. DIA-009 declares SPY; DIA-014 declares IWM; DIA-015 and DIA-018 declare
^VIX; and DIA-016 declares QQQ. Their existing pairs, divergence, direction,
and volatility-band calculations now consume only aligned historical auxiliary
frames from the verified bundle. All five migrations remain migration-pending
and do not advance latest results or followup qualification.

IWM-009 declares SPY for its small-cap momentum-rotation comparison. Its
existing relative-strength and pullback calculations now consume only the
aligned historical auxiliary frame supplied by the verified bundle. The
migration remains migration-pending and does not advance latest results or
followup qualification.

TLT-008, TLT-009, TLT-013, TLT-014, TLT-015, and TLT-016 form the rate/credit
auxiliary wave. TLT-008 declares IEF; TLT-009 declares ^TNX; TLT-013 declares
^MOVE; TLT-014 and TLT-016 declare ^MOVE plus SPY; and TLT-015 declares
^MOVE, SPY, and HYG. Their existing duration-spread, yield-velocity,
implied-volatility, equity-divergence, credit-divergence, and multi-window
direction calculations now consume only aligned historical auxiliary frames
from the verified bundle. All six migrations remain migration-pending and do
not advance latest results or followup qualification.

TQQQ-019, TQQQ-020, TQQQ-021, TQQQ-022, TQQQ-023, TQQQ-026, and TQQQ-027 form
the leveraged-tech auxiliary wave. TQQQ-019 and TQQQ-020 declare ^VIX;
TQQQ-021 declares ^MOVE; TQQQ-022 declares QQQ and SPY; TQQQ-023 declares
^TYX and ^TNX; TQQQ-026 declares SQQQ; and TQQQ-027 declares QQQ. Their
existing volatility, cross-asset, yield-curve, inverse-pair, and single-day
reversal calculations now consume only aligned historical auxiliary frames
from the verified bundle. All seven migrations remain migration-pending and
do not advance latest results or followup qualification.

USO-025, USO-026, USO-027, and USO-028 form the commodity-volatility wave.
USO-025, USO-027, and USO-028 declare ^OVX; USO-026 declares ^OVX and XLE.
Their existing implied-volatility, cross-asset, and multi-period capitulation
calculations now consume only aligned historical auxiliary frames from the
verified bundle. All four migrations remain migration-pending and do not
advance latest results or followup qualification.

XBI-008, XBI-017, XBI-019, and XBI-020 form the biotech auxiliary wave. XBI-008
declares IBB; XBI-017 and XBI-020 declare ^VIX; and XBI-019 declares ^VIX plus
XLV. Their existing pairs, volatility-band, sector-parent, and volatility-
direction calculations now consume only aligned historical auxiliary frames
from the verified bundle. All four migrations remain migration-pending and do
not advance latest results or followup qualification.

XLU-013 and XLU-014 form the utility/rates auxiliary wave. XLU-013 declares
^MOVE; XLU-014 declares ^MOVE and ^TNX. Their existing implied-volatility and
rate-direction calculations now consume only aligned historical auxiliary
frames from the verified bundle. Both migrations remain migration-pending and
do not advance latest results or followup qualification.

SIVR-009, SIVR-019, and SIVR-020 form the silver auxiliary wave. SIVR-009
declares GLD; SIVR-019 declares ^GVZ; and SIVR-020 declares UUP. Their existing
ratio-reversion, volatility-direction, and USD-regime calculations now consume
only aligned historical auxiliary frames from the verified bundle. All three
migrations remain migration-pending and do not advance latest results or
followup qualification.

COPX-013, COPX-014, COPX-015, COPX-016, COPX-017, and COPX-019 form the
commodity-miners macro/underlying wave. COPX-013 declares SPY and ^VIX;
COPX-014 declares GLD; COPX-015 declares ^VIX; COPX-016 declares DX-Y.NYB;
COPX-017 declares ^TYX and ^TNX; and COPX-019 declares HG=F. Their existing
macro, divergence, volatility, yield-curve, and copper-direction calculations
now consume only aligned historical auxiliary frames from the verified bundle.
All six migrations remain migration-pending and do not advance latest results
or followup qualification.

DIA-019, IWM-015, NVDA-016, TQQQ-004, TQQQ-005, TQQQ-007, TQQQ-012,
TQQQ-014, TQQQ-015, XBI-016, XLU-005, XLU-006, and XLU-007 form the final
legacy DataFetcher auxiliary wave. DIA-019 and IWM-015 declare QQQ; NVDA-016
declares SMH; TQQQ-004, TQQQ-005, and TQQQ-014 declare ^VIX; TQQQ-007,
TQQQ-012, and TQQQ-015 declare QQQ; XBI-016 declares QQQ; and XLU-005,
XLU-006, and XLU-007 declare TLT, TLT, and SPY respectively. Their existing
macro-confirmation, volatility-filter, capitulation, breakout, and relative-
value calculations now consume only aligned historical auxiliary frames from
the verified bundle. All thirteen migrations remain migration-pending and do
not advance latest results or followup qualification. This wave also removes
the last experiment-scoped market-data bypass findings from the migration
allowlist; the static scanner now reports zero direct or indirect bypasses.

CIBR-001 through CIBR-005, CIBR-007 through CIBR-013, and CIBR-015/016 form
the first post-bypass primary-only asset wave. Each strategy now declares its
single adjusted-daily CIBR dependency, captures its local detector and shared
bundle executor in the immutable definition, and runs through the provider-free
primary bundle seam. Their migration runs remain pending and do not advance
latest results, followup qualification, or lifecycle state. CIBR-014 remains
on its explicit tracer implementation and is covered by the same primary-only
contract separately.

DIA-001 through DIA-008, DIA-010 through DIA-012, and DIA-017 form the next
primary-only asset wave. Each strategy now declares its single adjusted-daily
DIA dependency, captures its local detector and shared bundle executor in the
immutable definition, and runs through the provider-free primary bundle seam.
Their migration runs remain pending and do not advance latest results,
followup qualification, or lifecycle state.

FCX-001 through FCX-005, FCX-007, and FCX-009 through FCX-014 form the next
primary-only asset wave. Each strategy now declares one adjusted-daily FCX
dependency and uses the shared provider-free bundle execution and immutable
definition boundary. These migrations remain pending and do not advance
latest results, followup qualification, or lifecycle state.

EWJ-001, EWJ-003, EWJ-005, EWT-002 through EWT-006, EWT-008/009, and
EWZ-001 through EWZ-004 plus EWZ-007 form the Japan/Taiwan/Brazil primary-only
wave. Each strategy now declares one adjusted-daily primary dependency and
uses the shared provider-free bundle execution and immutable definition
boundary. These migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

FXI-001 through FXI-004, FXI-006, and FXI-008 through FXI-014 form the next
primary-only China ETF wave. Each strategy now declares one adjusted-daily FXI
dependency and uses the shared provider-free bundle execution and immutable
definition boundary. These migrations remain pending and do not advance latest
results, followup qualification, or lifecycle state.

GLD-001 through GLD-014 and IBIT-001 through IBIT-009 form the commodity and
crypto primary-only wave. Each strategy now declares one adjusted-daily
primary dependency and uses the shared provider-free bundle execution and
immutable definition boundary. These migrations remain pending and do not
advance latest results, followup qualification, or lifecycle state.

SIVR-001 through SIVR-005, SIVR-007/008, and SIVR-010 through SIVR-018 form
the silver primary-only wave. Each strategy now declares one adjusted-daily
SIVR dependency, preserves its existing execution-model/backtester variant,
and uses the shared provider-free bundle execution and immutable definition
boundary. SIVR-006 was already migrated as the followup primary slice, while
SIVR-009/019/020 remain on their previously migrated auxiliary declarations.
All sixteen new migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

TSLA-001 through TSLA-016 form the Tesla primary-only wave. Each strategy now
declares one adjusted-daily TSLA dependency, preserves its existing
execution-model/backtester variant, and uses the shared provider-free bundle
execution and immutable definition boundary. TSLA-017 through TSLA-020 remain
on their previously migrated auxiliary declarations. All sixteen new
migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

VOO-001, VOO-002, and VOO-004 through VOO-006 form the VOO primary-only wave;
VOO-003 was already migrated. Each strategy now declares one adjusted-daily VOO
dependency, preserves its existing execution-model/backtester variant, and
uses the shared provider-free bundle execution and immutable definition
boundary. The five new migrations remain pending and do not advance latest
results, followup qualification, or lifecycle state.

The first VOO tracer replay also passed. VOO-001 used snapshot
`ea33ffb51e318408675549b451d97c6eff9718965a813aa1db0c663714f3637c` with
parity digest `438deb343b6522d4d5b2be866015cec06d17079d7a2f4e69c9b1110745718c44`.
Indicators, signal dates, and filled trades matched exactly; its migration
result remains `migration-pending` and leaves `latest.json` and qualification
state unchanged.

SPY-001, SPY-002, SPY-004 through SPY-006, and SPY-008/009 now form the
remaining SPY primary-only wave around the already-migrated SPY-003 auxiliary
declaration and SPY-007 tracer. Each declares one adjusted-daily SPY dependency
and preserves its existing execution-model or trailing-stop backtester. These
seven migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

TSM-001 through TSM-005 and TSM-010 form the remaining TSM primary-only wave;
TSM-006 was already migrated as the primary momentum slice, while TSM-007/008
and TSM-011 through TSM-022 remain on their previously migrated auxiliary
declarations. Each new strategy declares one adjusted-daily TSM dependency and
preserves its existing execution-model/backtester variant. These six migrations
remain pending and do not advance latest results, followup qualification, or
lifecycle state.

TLT-001 through TLT-007 and TLT-010 through TLT-012 form the TLT primary-only
wave. TLT-008/009 and TLT-013 through TLT-017 remain on their previously
migrated auxiliary declarations. Each new strategy declares one adjusted-daily
TLT dependency and preserves its existing execution-model/backtester variant.
These ten migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

XLU-001, XLU-003, XLU-004, XLU-008, XLU-009, and XLU-010 through XLU-012 form
the remaining XLU primary-only wave; XLU-002 was already migrated as the
primary capped-pullback slice, while XLU-005 through XLU-007 and XLU-013/014
remain on their previously migrated auxiliary declarations. Each new strategy
declares one adjusted-daily XLU dependency and preserves its existing
execution-model/backtester variant. These eight migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

VGK-001, both VGK-002 variants, VGK-003 through VGK-006, and VGK-008 form the
VGK primary-only wave; VGK-007 and VGK-009 remain on their previously migrated
primary/auxiliary declarations. Each new strategy declares one adjusted-daily
VGK dependency and preserves its existing execution-model/backtester variant.
These eight migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

INDA-001 through INDA-006, INDA-008/009, and INDA-011 form the remaining INDA
primary-only wave. INDA-007 and INDA-012 through INDA-015 remain on their
previously migrated auxiliary declarations. Each new strategy declares one
adjusted-daily INDA dependency and preserves its existing
execution-model/backtester variant. These nine migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

SOXL-001 through SOXL-004, SOXL-006, SOXL-008/009, and SOXL-012/013 form the
remaining SOXL primary-only wave; SOXL-005 was already migrated. Each new
strategy declares one adjusted-daily SOXL dependency and preserves its existing
execution-model/backtester variant. These nine migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

URA-001, URA-002, and URA-004 through URA-005, URA-007 through URA-014 form
the remaining URA primary-only wave; URA-003/006 were already migrated as
primary/auxiliary slices. Each new strategy declares one adjusted-daily URA
dependency and preserves its existing execution-model/backtester variant.
These twelve migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

COPX-001 through COPX-003, COPX-005/006, COPX-008 through COPX-012, and
COPX-018 form the remaining COPX primary-only wave; COPX-007 was already
migrated as the primary volatility-adaptive slice, while COPX-013 through
COPX-019 remain on their previously migrated auxiliary declarations. Each new
strategy declares one adjusted-daily COPX dependency and preserves its existing
execution-model/backtester variant. These eleven migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

EEM-001 through EEM-005, EEM-007 through EEM-011, EEM-013 through EEM-015, and
EEM-021 form the remaining EEM primary-only wave; EEM-006, EEM-016 through
EEM-020, and EEM-022 remain on their previously migrated auxiliary declarations,
while EEM-012 was already migrated as the primary slice. Each new strategy
declares one adjusted-daily EEM dependency and preserves its existing
execution-model/backtester variant. These fourteen migrations remain pending
and do not advance latest results, followup qualification, or lifecycle state.

IWM-001 through IWM-005, IWM-007/008, and IWM-010 through IWM-014 form the
remaining IWM primary-only wave; IWM-006 was already migrated as the primary
BB-squeeze slice, while IWM-009 and IWM-015 remain on their previously migrated
auxiliary declarations. Each new strategy declares one adjusted-daily IWM
dependency and preserves its existing execution-model/backtester variant. These
twelve migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

NVDA-001 through NVDA-005, NVDA-009 through NVDA-013, and NVDA-017/019/020 form
the remaining NVDA primary-only wave; NVDA-006 through NVDA-008, NVDA-014 through
NVDA-016, NVDA-018, and NVDA-021 remain on their previously migrated auxiliary
declarations. Each new strategy declares one adjusted-daily NVDA dependency and
preserves its existing execution-model/backtester variant. These thirteen
migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

USO-001, USO-005, USO-007, USO-010, USO-012/013, USO-021 through USO-024, and
USO-029 form the remaining USO primary-only wave; USO-009 was already migrated
as the primary momentum slice, while USO-025 through USO-028 remain on their
previously migrated ^OVX/XLE auxiliary declarations. Each new strategy declares
one adjusted-daily USO dependency and preserves its existing
execution-model/backtester variant. These eleven migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

XBI-001, XBI-004 through XBI-007, and XBI-009 through XBI-015 form the remaining
XBI primary-only wave; XBI-008 and XBI-016 through XBI-020 remain on their
previously migrated IBB/QQQ/^VIX/XLV auxiliary declarations. Each new strategy
declares one adjusted-daily XBI dependency and preserves its existing
execution-model/backtester variant. These twelve migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

As of 2026-08-07, the primary-only followup contract covers 285 experiment
entries (571 test cases including the module-level contract checks), and the
full repository regression passes 1226 tests. The only remaining direct
`ExecutionModelStrategy` classes are the intentional CIBR-014/SPY-007 tracer
implementations and nine TQQQ variants outside the primary followup contract;
they remain explicitly out of this shared-mixin migration boundary. No result,
latest, qualification, or lifecycle state is changed by these code-only waves.

The current trial registry additionally contains five migration-mode
observations: the original SPY-007, SIVR-001, TSLA-001, and VOO-001 records plus
the current-definition SPY-007 replay. All remain `migration-pending` and are
not valid formal observations for qualification or Shadow registration. SPY-007
also has one separate valid offline observation, recorded in the canonical
status section above; no qualification or lifecycle state has been created.
