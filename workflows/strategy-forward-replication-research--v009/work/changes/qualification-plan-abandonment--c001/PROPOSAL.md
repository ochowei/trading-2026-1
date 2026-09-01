# Qualification Plan Abandonment Proposal

## Current problem

The qualification registry permits one open forward or retrospective plan per experiment family.
An open plan becomes terminal only when a canonical `historical_screen` event is appended. If the
owning workflow study is cancelled before a screen can be produced, the study lifecycle and
qualification lifecycle diverge: the cancelled study cannot resume, but its plan remains
`historical-screen-pending` and permanently blocks a corrected successor study in the same family.

This happened after v009 S002 disclosed an underspecified next-open execution envelope. Its screen
failed closed before registry mutation and the study was correctly cancelled. S003 corrected the
frozen envelope, but its guarded plan registration was then rejected because S002's append-only plan
still has no terminal event. The repository currently has no canonical plan-abandonment event or
public command. Deleting the local registry, fabricating a screen, changing the family identity, or
weakening the single-open-plan guard would destroy the audit boundary.

## Proposed workflow change

Add a narrow, append-only qualification-plan abandonment capability to the next workflow version:

- Introduce canonical event type `historical_plan_abandoned` with event identity
  `historical-plan-abandoned:<plan-id>`.
- Add guarded command `trading qualification plan abandon` that accepts the exact plan identity,
  exact authorizing workflow version, stable human approver, and concrete reason. The authorizing
  version must be active, effective, and released with capability
  `qualification-plan-abandonment-v1`; therefore landing the implementation cannot make v009
  capable of abandonment. The writer derives rather than trusts the owning study path and all
  plan/workflow/family identities from the verified registry and frozen study.
- Permit abandonment only when the plan has no historical screen, has no prior abandonment event,
  and its exact owning study is already terminal `cancelled`. A paused, running, preregistered,
  awaiting-review, completed, missing, mismatched, or legacy plan without exact study binding is
  ineligible.
- Persist current UTC time, approver, reason, plan identity, experiment family, frozen study path,
  preregistration/specification/freeze identities, exact authorizing workflow release and
  capability, prior registry head, and canonical event-chain linkage. Publication is atomic and
  add-only under the existing qualification-registry lock.
- Treat either a canonical historical screen or a canonical abandonment event as closing the plan
  for the single-open-plan invariant. Never treat study cancellation alone as registry evidence.
- Reject any later screen, Shadow registration, replay attachment, second abandonment, or plan
  revival for an abandoned plan. Abandonment supplies no outcome, disposition, Evaluation,
  promotion, broker, order, position, or live authority.
- Extend status, registry verification, checkpoint replay, tracked qualification-evidence
  snapshots, and terminal validators so the new event is explicit and tamper-evident.

## Expected effect

The repository can preserve every invalid plan byte while safely releasing the family-level lock
after the owning study has already been cancelled. A corrected successor still requires its own
workflow version, CLI-allocated study identity, preregistration, stage authorities, candidate
freeze, and qualification plan. The abandonment event is administrative terminal evidence only;
it cannot convert prior evidence into a screen result or change a study outcome.
