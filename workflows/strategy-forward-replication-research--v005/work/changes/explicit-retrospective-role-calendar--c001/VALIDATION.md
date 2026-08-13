# Validation

## Evidence and challenge method

Provider-free implementation validation completed without market-data refresh, snapshot, strategy
execution, metric, screen, or outcome inspection.

- `uv run pytest -q tests/test_historical_qualification.py tests/test_qualification_workflow.py
  tests/test_qualification_cli.py tests/test_qualification_registry.py tests/test_result_schema.py`:
  55 passed.
- The focused suite covers the exact FXI calendar shape: 2009 warmup only, 2010-2014 retrospective
  evaluation, and 2015-2025 Development context. It also covers partial overrides, role overlap,
  incomplete chronology, CLI routing, registry round-trip, result-schema validation, completed-
  context timing, and old payloads that omit `role_calendar`.
- `uv run ruff check src/ tests/`: passed.
- `uv run ruff format --check src/ tests/`: 1,886 files already formatted.
- `uv run trading workflow sync`: completed.
- `uv run trading workflow validate --all`: passed.
- `uv run trading policy validate --all`: passed.
- A full `uv run pytest -q` sample was stopped after 4 minutes 35 seconds because the repository
  suite is long-running; 129 tests had passed with no failures at interruption. The complete focused
  behavioral suite above subsequently passed after the final compatibility adjustment.

Existing default plans still omit the optional field from their persisted payload. Registry and
result validation accept the original immediately-preceding chronology, including additional
earlier complete Development years, while rejecting later or otherwise nonstandard chronology
without the explicit calendar.

## Interaction with other accepted changes

There are no other v005 change records. This change is evaluated independently and leaves the
released v005 normative dependency bytes unchanged. The proposed v006 contract is isolated in
`docs/historical-qualification-and-shadow-v006.md`.

## Remaining uncertainty

The complete repository test suite was sampled rather than run to completion; the planner's direct
and persistence surfaces are fully covered by the focused suite. Human acceptance,
replacement-version approval, release preparation, canonical-branch merge, and the successor
study's separate cancellation, preregistration, candidate-freeze, and execution approvals remain
outstanding.
