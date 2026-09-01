# Validation

Before acceptance and v009 evolution, validation must demonstrate provider-free that:

1. the exact-study compiler derives only the pinned 2013 warmup, 2014-2018 Development, 2019
   quarantine, 2020-2024 annual Evaluation folds, and 2025 replay session inventories;
2. caller-supplied date, year, fold, route, or role overrides fail before registry or evidence
   mutation;
3. incomplete asset history, missing sessions, overlap, or unexpected sessions fail closed without
   partial ranking or partial publication;
4. candidate freeze precedes Evaluation and replay, and neither interval can influence selection;
5. the 2025 operation is provider-free, plan-bound, ordered, idempotent, and atomically publishes
   non-actionable replay evidence without Shadow registration or authority widening;
6. fewer than 12 completed replay fills and any complete frozen replay gate failure map to `fail`,
   while identity or replay-integrity defects map to `indeterminate`;
7. the only positive terminal disposition is `retrospectively-supported`, and no result can produce
   `shadow-eligible`, `activation-eligible`, Controlled Activation, Active, broker, order, or live
   authority;
8. existing v001-v008 workflows, frozen studies, route schemas, calendars, results, and historical
   path resolution continue to validate and replay without byte or semantic reinterpretation; and
9. the combined v009 release tests still cover C001-C004 plus this change, including fresh-checkout
   resolution and exact-version action guards.

Run workflow and policy validation, focused workflow-authoring/control-state/fixed-calendar tests,
the affected qualification and terminal-evidence suites, repository fast regression, generated
index synchronization, and whitespace validation before recording an acceptance decision.

## Post-acceptance implementation evidence (2026-09-01)

This evidence was produced after acceptance and v009 evolution; it preserves that sequencing and
does not reinterpret the accepted proposal as prior implementation proof. The v009 draft now
requires the `fixed-calendar-retrospective-v1` capability and exact workflow-owned calendar:
2013 warmup, 2014-2018 Development, 2019 quarantine, five annual 2020-2024 Evaluation folds, and
2025 retrospective execution replay. Any route or calendar drift fails preregistration.

`src/trading/workflow/retrospective_replay.py` and
`trading qualification replay run-study` implement the plan-bound 2025 operation. It requires a
passing Historical Evaluation and challenge manifest, exact offline formal observation, complete
2025 XNYS sessions, frozen fingerprint and policies, and publishes only non-actionable paper
proposals, simulated fills, ledger-style events, metrics, checkpoints, drift and gates. Publication
is content-addressed and atomic; exact retry is idempotent; the artifact embeds the raw replay input
needed for provider- and definition-free recomputation. Fewer than 12 completed fills is encoded as
a failed gate.

Provider-free synthetic coverage demonstrates dry-run zero publication, atomic two-file output,
exact retry idempotence, collision rejection, injected rename failure without a visible partial
directory, and independent artifact recomputation. Exact-calendar, route-specific capability,
terminal-stage, failure-disposition, and v001-v008 compatibility regressions are included in the
affected 187-test set. Repository validation completed with:

- `uv run pytest -q tests/test_retrospective_replay.py`: 4 passed;
- the affected qualification/workflow/terminal/result/path suites: 187 passed;
- `uv run pytest -m "not slow" -q`: 764 passed, 770 deselected;
- `uv run pytest -m legacy_conformance -n auto -q`: 811 passed;
- `uv run ruff check ...` and `uv run ruff format --check ...`: passed;
- `uv run trading workflow validate --all`: passed; and
- `uv run trading policy validate --all`: passed.

No study was started, no outcome was inspected, and no Shadow, activation, broker, order, live,
release, or workflow activation authority was created.
