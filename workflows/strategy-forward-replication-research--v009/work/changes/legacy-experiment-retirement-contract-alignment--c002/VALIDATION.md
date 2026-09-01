# Validation

## Evidence and challenge method

Pre-acceptance review verified the canonical architecture, ADR, retirement contract,
result/archive documentation, migration registry, maintained resolver, and focused positive and
negative tests for the terminal legacy archive and bounded schema-2 path resolution. A later
post-acceptance branch review found that the resolver enforced hop count, cycle, and digest
identity but did not reject a two-hop chain with reversed migration versions or an arbitrary
cross-artifact-class transition.

The remediation now requires every two-hop chain to be exact `v009 -> v010`. Artifact classes must
remain identical except for the one pre-existing, digest-bound transition from the exact
categorized `trial-registry` path to its exact `trial-registry-history` path. That narrow exception
preserves the append-only registry and immutable study evidence; all legacy-result chains remain
same-class and every other cross-class transition fails closed.

Post-remediation validation results on 2026-09-01:

- `uv run pytest -p no:cacheprovider -q tests/research/test_result_paths.py`: 11 passed, including
  wrong-version-order, arbitrary cross-class, and exact registry-history transition coverage.
- `uv run pytest -p no:cacheprovider -q tests/research/test_result_paths.py tests/legacy/test_result_diagnostics.py tests/legacy/test_result_evaluation.py tests/legacy/test_followup_backtest_cli.py tests/legacy/test_namespace_compatibility.py tests/test_workflow_authoring.py tests/workflow/test_workflow_release_activation.py tests/workflow/test_workflow_control_state.py tests/workflow/test_workflow_safety_assessment.py tests/repository_checks/test_path_ownership.py`: 144 passed.
- `uv run pytest -p no:cacheprovider -m 'not slow' -q`: 787 passed, 770 deselected.
- `uv run pytest -p no:cacheprovider -m legacy_conformance -n auto -q`: 811 passed.
- `uv run ruff check --no-cache src/ tests/research/test_result_paths.py`: passed.
- `uv run ruff format --check --no-cache src/ tests/research/test_result_paths.py`: 163 files
  already formatted.
- `uv run trading workflow validate --all`: passed.
- `uv run trading policy validate --all`: passed.
- `uv run python config/repository-checks/check_path_ownership.py`: passed.
- `uv run python config/repository-checks/check_legacy_experiment_inventory.py`: passed.
- `git diff --check` and `git diff --cached --check`: passed.
- `results/experiment-results/` is absent, while tracked retirement mappings resolve to retained
  `legacy/results/` bytes through the tested bounded resolver.

The exact control states remain v009 `N05` and v010 `N02`. C002 creation and post-acceptance
remediation changed only the change record and its retained source/request files, the generated
v009 work index, the v010 draft/source/request, and the resolver plus focused tests. No study,
qualification registry, result artifact, release evidence, activation evidence, broker state,
order, or position was changed.

## Interaction with other accepted changes

At pre-acceptance validation time, v009/C001 was the only accepted source change. C002 was then
independently accepted by `ochowei@gmail.com` at `2026-09-01T10:50:13.870748Z`. C001 governs
append-only qualification-plan abandonment; C002 governs legacy-result retirement and
digest-bound path compatibility. Their authorities remain independent. C002 repeats the safe
version-boundary facts for v009/S001, S002, and S003 and preserves S003's `restart-on-v010`
decision, but it neither invokes C001 nor closes S002's open plan.

After acceptance, the guarded evolve façade collected both accepted changes and updated the
existing v010 draft as one complete self-contained contract. It added
`docs/legacy-experiment-retirement-v010.md` as a normative dependency, removed the stale
single-hop/current-`results/experiment-results/` claims, and left released v009 bytes unchanged.

## Remaining uncertainty

C002 has its independent accepted decision, and v010 has been re-evolved from C001 and C002. v010
remains a draft: it has not been prepared or activated, no positive release-evidence digest for the
updated dependency set exists, and no S002 plan abandonment has occurred. Release preparation,
Workflow Release Activation, plan abandonment, successor-study creation, and every study-stage
approval remain separate authorities that must be exercised only through their guarded commands.
