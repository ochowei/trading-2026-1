# Validation

## Evidence and challenge method

Implementation adds the canonical `historical_plan_abandoned` registry event, guarded
`qualification plan abandon` CLI route, exact cancelled-study resolver, effective-release
capability resolver, explicit status projection, single-open-plan closure, later-screen rejection,
terminal-evidence rejection, hash-chain replay validation, and the proposed v010 qualification
addendum. The event binds the original frozen study hashes, current cancelled lifecycle identity,
exact authorizing workflow release/capability, current human approval and reason, and prior registry
head.

Focused positive and negative tests cover successful append, exact event/prior-head content,
family-lock release, duplicate abandonment, every non-cancelled study status, missing or
non-canonical approval/reason, mismatched study path/workflow, absent capability, legacy plans,
already-screened plans, later-screen rejection, status output, CLI argument routing, and effective
release capability resolution. Results:

- `uv run pytest -q tests/test_qualification_registry.py tests/test_qualification_cli.py tests/test_qualification_plan_abandonment.py tests/test_study_terminal_evidence.py`: 54 passed.
- `uv run ruff check src/`: passed.
- `uv run ruff format --check src/`: 162 files already formatted.
- `uv run pytest -m 'not slow'`: 784 passed, 770 deselected.
- `uv run trading workflow validate --all`: passed.
- `uv run trading policy validate --all`: passed.
- `git diff --check`: passed.

A direct negative command against v009 failed before registry creation with `effective workflow
release does not authorize qualification-plan abandonment`; the temporary target registry did not
exist afterward. This confirms that installing the implementation does not grant v009 the new
authority.

## Interaction with other accepted changes

There are no other accepted changes aggregated into this implementation. C001 is accepted by its
separate human decision after validation. The implementation does not edit released v009 workflow
or release bytes and does not change S001, S002, S003, or the current qualification registry. S002
remains `cancelled` with its plan open; S003 remains `paused` and its version-boundary disposition
remains `restart-on-v010`.

## Remaining uncertainty

No v010 workflow has been accepted, prepared, released, merged, or activated, so the positive
effective-release gate is tested with an isolated repository double rather than an active v010.
No abandonment event has been appended to the real qualification registry. Successor evolution,
release-safety review, release preparation, activation, and a separate current approval for the
exact S002 plan abandonment all remain required. Abandonment supplies no Evaluation outcome,
screen disposition, replay, Shadow, broker, order, position, or live authority.
