# Proposal

## Current problem

The v006 workflow requires a retrospective-confirmatory plan to freeze a current-time
`retrospective_selection_checkpoint`. That checkpoint records the selected trial, complete family,
baseline relationship, freeze time, and prior-selection-history disclosure without pretending to
be a future-only Forward Selection Epoch.

Production registration and screen coordination understand this boundary. The family-wise
selection-adjustment evaluator does not: when global registry history is incomplete, it consults
only `forward_selection_epoch` and rejects a valid retrospective checkpoint before computing the
screen. Existing provider-free tests verify retrospective registration and coordination but do not
exercise the complete registration-to-selection-adjustment path with prior history explicitly
incomplete. This mismatch caused v006/S001 to complete `indeterminate`; it cannot be repaired by
changing the pinned verifier after its 2010-2014 outcomes were exposed.

## Proposed workflow change

Define a common frozen selection boundary for family-wise adjustment. It is exactly one of:

- a `forward_selection_epoch` for clean Historical evidence; or
- a `retrospective_selection_checkpoint` for retrospective-confirmatory evidence.

When prior selection history is incomplete, the evaluator must require the boundary's explicit
disclosure, exact included trial IDs, exact selected trial, and registration timestamps no later
than the boundary time. It must use `started_at` for a forward epoch and `frozen_at` for a
retrospective checkpoint. The two boundary types remain semantically distinct: a retrospective
checkpoint never becomes forward-clean evidence or promotion authority.

Require release-readiness validation to run provider-free through the public production path from
retrospective plan registration to family-wise screen selection adjustment. The regression must
cover prior incomplete history, exact complete-family inputs, selected-trial identity, timestamp
ordering, boundary-type exclusivity, and fail-closed rejection for missing, mismatched, late, or
incomplete evidence. Registration-only or coordinator-only coverage is insufficient.

Do not rewrite v006, v006/S001, its completion evidence, or any prior registry event. Do not rerun
v006/S001 or reuse its exposed 2010-2014 period as confirmation for a changed lineage.

## Expected effect

A replacement workflow can preregister and screen a future retrospective-confirmatory study using
the same frozen selection semantics end to end. Clean Historical behavior remains unchanged, and
retrospective evidence remains non-promotional. Release validation will fail before release if the
planner, persistence, coordinator, and evaluator disagree about either selection-boundary type.
