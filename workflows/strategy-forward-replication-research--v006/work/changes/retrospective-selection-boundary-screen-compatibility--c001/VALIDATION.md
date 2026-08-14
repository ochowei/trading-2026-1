# Validation

## Evidence and challenge method

Provider-free implementation validation repaired the contract/implementation mismatch without
refreshing market data, running a strategy definition, executing a formal run, or inspecting any
new outcome:

- `docs/historical-qualification-and-shadow-v006.md` requires retrospective registration to freeze
  `retrospective_selection_checkpoint` and preserve its non-forward semantic role.
- `src/trading/core/qualification_workflow.py` selects either the forward epoch or retrospective
  checkpoint when identifying the selected trial and frozen family.
- Before the repair, `src/trading/core/qualification.py` derived incomplete-history acceptance
  only from `forward_selection_epoch` inside `evaluate_family_selection_adjustment`.
- `evaluate_family_selection_adjustment` now resolves one common frozen boundary: the forward epoch
  or retrospective checkpoint. It validates the boundary's history disclosure, exact family,
  selected trial, registration timestamps, and boundary-specific time (`started_at` or `frozen_at`).
- The focused domain test covers a prior-incomplete retrospective checkpoint and verifies that the
  family-wise adjustment succeeds with the exact frozen universe.
- The public `run_registered_historical_screen` regression now runs both forward-epoch and
  retrospective-checkpoint variants. The retrospective variant uses the public plan-registration
  coordinator, persists and reloads the plan, uses an incomplete legacy registry, reaches the
  actual family-wise evaluator, and records its expected downstream screen result.
- Production-path negative regressions corrupt the persisted trial-registry view after a valid
  retrospective registration and prove fail-closed rejection of disclosure mismatch, changed
  family universe, missing registration timestamps, and late registrations. Domain regressions
  separately cover selected-trial mismatch and the same boundary guards at the evaluator surface;
  plan-construction tests cover missing or dual boundary rejection.
- Qualification-registry tests prove that typed registration rejects dual boundaries and that
  payload reload rejects both missing retrospective and dual boundaries, preventing persistence
  from bypassing builder validation or silently preferring the forward boundary.
- Completed v006/S001 preserves the exact fail-closed symptom and was independently concluded
  `indeterminate`; it is defect evidence only and will not be rerun or repurposed as validation.

The completed provider-free validation demonstrates:

1. successful end-to-end registration and selection adjustment for an exact retrospective
   checkpoint whose prior selection history is disclosed as incomplete;
2. unchanged forward-epoch behavior;
3. rejection of absent or dual boundaries, disclosure mismatch, changed family universe, changed
   selected trial, missing registration timestamps, and trials registered after the applicable
   boundary time;
4. unchanged serialization and deterministic identities for existing plan payloads; and
5. workflow, policy, lint, formatting, and focused qualification test success.

Commands and results:

- `.venv/bin/pytest -q tests/test_historical_qualification.py tests/test_qualification_workflow.py
  tests/test_qualification_cli.py tests/test_qualification_registry.py tests/test_result_schema.py`:
  `68 passed`.
- `.venv/bin/ruff check src/trading/core/qualification.py
  src/trading/core/qualification_workflow.py
  src/trading/research_data/qualification_registry.py tests/test_historical_qualification.py
  tests/test_qualification_workflow.py tests/test_qualification_registry.py`: passed.
- `.venv/bin/ruff format --check` on the same six modified Python files: passed; all already
  formatted.
- `.venv/bin/trading workflow sync`: completed.
- `.venv/bin/trading workflow validate --all`: passed.
- `.venv/bin/trading policy validate --all`: passed.

The implementation changes are ordinary repository code and tests at their authoritative paths;
no code or test artifact was copied into `workflows/`. The v007 draft pins the new normative
`docs/historical-qualification-and-shadow-v007.md`, and `docs/ARCHITECTURE.md` records the versioned
Phase 6 document pattern without rewriting the v006 dependency.

## Interaction with other accepted changes

There are no other v006 change records. This draft is evaluated independently. If another change
is accepted before replacement release preparation, combined impact and test coverage must be
reassessed in the single next-version draft.

## Remaining uncertainty

The complete repository test suite has not been run to completion in this change. C001 is accepted
and its wording is incorporated in the v007 draft; release preparation, canonical-branch merge,
and effectiveness remain outstanding. No outcome-relevant rerun of v006/S001 is permitted or
required.
