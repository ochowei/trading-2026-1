# Validation

## Evidence and challenge method

Provider-free shared-tooling validation is complete. The confirmed design boundary and
explanatory source are recorded
in `docs/research-evidence-stages-and-outcomes.md`: a study-time retrospective pass may complete a
study and record `retrospectively-supported`, but it cannot grant Shadow, activation, or live
authority. Future verified-clean evidence belongs to an independently preregistered successor.

The implementation and relevant regressions demonstrate:

1. a released structured capability, rather than string matching, authorizes the route;
   preregistration freezes and hashes `QUALIFICATION_SPEC.json` with a chronological
   Development/retrospective Evaluation calendar before either stage performs outcome-relevant
   work; its preregistration validator rejects incomplete warmup, family roles/source hashes,
   shared sources, execution dependencies, benchmark/bootstrap budgets, history disclosures, or
   challenge targets/gates before candidate freeze;
2. Development retains complete family history and freezes exactly one candidate plus a distinct
   baseline before retrospective inspection;
3. public registration, durable human approval/provenance disclosure, persistence/reload, offline
   screen coordination, family-wise selection adjustment, complete frozen challenge-family
   identities, and terminal evidence agree on exact identities;
4. the route requires at least three complete Development years and five complete consecutive
   annual Evaluation folds, then enforces the unchanged v007 trade, fold, return, profit-factor,
   preregistered stress-drawdown, concentration, and selection-adjustment floors; it also requires
   the v007 cash, distinct-baseline, random-entry, parameter, execution, cost/fill, missed-entry,
   and regime challenge set while treating each study's baseline margins, binding requirements,
   drawdown limit, and other hypothesis-specific gates only as preregistered per-study constraints;
5. a complete Development failure requires a linked complete and trustworthy Development gate,
   rejects an actual candidate-freeze artifact, and requires a tracked snapshot of the
   preregistered authoritative qualification registry whose bytes equal the current registry head
   at completion and contain no plan/screen for the study; deleting a freeze after plan creation is
   rejected before projecting `development-selection-failed`. Completion and registration share
   one lock through terminal commit, registration re-loads freeze/completion state inside the lock,
   and completion rejects a pending transaction journal;
6. complete passing retrospective evidence projects study `pass` plus only
   `retrospectively-supported` after `TERMINAL_EVIDENCE.json` verifies the exact study,
   preregistration, spec, candidate freeze, tracked content-addressed registry/checkpoint snapshot,
   authoritative hash-chain replay, exact PLAN/release digests, typed folds/aggregate/benchmarks/
   selection adjustment, recomputed 14-gate screen, and exactly nine challenge gates with unique
   frozen targets and distinct evidence artifacts whose own observed values drive gate replay;
   missing, duplicate, or noncanonical screens and missing challenges fail closed; snapshot
   publication rejects a physical registry path that differs from repository root plus its declared
   preregistered source identity,
   while a complete failed gate projects study `fail` plus only
   `retrospective-screen-failed`;
7. fixed retrospective screens reject `insufficient-evidence`, unmet trade/fold minimums are
   `fail`, and missing/inconsistent identity or evidence yields stage-identified `indeterminate`;
8. Shadow registration rejects every retrospective-only source, including a passing screen or
   completed `pass` study;
9. the existing exact `revisits` lifecycle remains the only successor link; the replacement
   workflow must require later unused Evaluation roles without relabeling prior outcomes; and
10. existing v007 payloads, clean Historical qualification, Shadow, activation, and monitoring
    retain their current behavior; and
11. release preparation pins the explanatory companion digest, fresh validation rejects any byte
    drift, and the docs pointer cannot become a second maintained copy.

The route is now an explicit persisted preregistration identity with exact artifact-digest
linkage. It requires earlier Development,
five later completed annual folds, a retrospective selection checkpoint, non-clean classification,
and the unchanged shared v007 threshold floors. `pass`, both forms of `fail`, and stage-identified
`indeterminate` have exact terminal disposition mappings; `insufficient-evidence` is rejected.
Result validity and qualification registries preserve the route after reload, and every
retrospective-only passing source is rejected for Shadow. Release tooling now supports a
`reference` dependency with `pinned: true`, records its SHA-256, and rejects post-release drift.

Validation performed on 2026-08-15 without provider or market-outcome access:

- `ruff check src tests`: passed;
- `ruff format --check src tests`: passed;
- the complete relevant regression set covering qualification domain, registry, coordinator, CLI,
  result validity, Shadow, trial registry, workflow authoring, followup guards, exact-study
  compilation, terminal evidence, immutable qualification evidence, and the evidence store: 259
  passed in 8.11 seconds. Exact invocation:

```text
UV_CACHE_DIR=/private/tmp/codex-uv-cache uv run pytest -q tests/test_historical_qualification.py tests/test_qualification_cli.py tests/test_qualification_registry.py tests/test_qualification_workflow.py tests/test_result_schema.py tests/test_trial_registry.py tests/test_workflow_authoring.py tests/test_study_qualification.py tests/test_study_terminal_evidence.py tests/test_research_evidence_store.py tests/test_shadow_qualification.py tests/test_followup_cutover.py tests/test_followup_cutover_cli.py tests/test_live_drift.py tests/test_live_drift_cli.py tests/test_live_drift_followup_integration.py tests/test_followup_manual_integration.py tests/test_research_run_coordinator.py
```

- `trading workflow validate --all`: passed;
- `trading policy validate --all`: passed; and
- `git diff --check`: passed.

Hypothesis-specific baseline margins, binding definitions, robustness metrics, and regime gates
remain preregistered study artifacts assessed from exact offline evidence; the shared tooling does
not invent one generic performance rule for heterogeneous strategies. It freezes and verifies the
complete identities, universal floors, and authority mapping those study-specific gates must obey.

## Interaction with other accepted changes

v007/C001 and v007/C002 are complementary but independently reviewed and accepted source changes:
C001 addresses frozen clean-Historical preservation and complete-family plan readiness; C002 adds
a terminal study-time retrospective route. A replacement release that combines them must preserve
the validated distinction between explicit clean and retrospective calendars, freeze both complete
families correctly, and prevent either route from borrowing the other's disposition or authority.

## Remaining uncertainty

No replacement workflow version exists yet. Although both source changes are accepted, the
explanatory guide has not yet moved beside a v008 `WORKFLOW.md`, the docs source has not yet become
a pointer, and no normative v008 contract authorizes this route. Those remain separate
release-authoring and release-approval steps, not permission to use the route under v007. The
current v007 release lacks the structured capability, so both study initialization and
qualification registration reject its use. Actual studies still require their own preregistration
and staged human outcome-work approvals.
