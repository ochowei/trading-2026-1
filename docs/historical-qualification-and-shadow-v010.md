# Historical Qualification and Shadow v010 Addendum

This addendum defines the append-only administrative termination of a Historical qualification
plan whose exactly bound workflow study is already terminal `cancelled`. It does not modify the
Historical Screen, Shadow, activation, broker, order, position, or live-authority contracts.

## Capability and command boundary

The public command is:

```text
trading qualification plan abandon \
  --plan-id <exact-plan-id> \
  --workflow <exact-active-workflow-version> \
  --approved-by <stable-human-identity> \
  --reason <concrete-reason>
```

The exact workflow version supplied by `--workflow` must be structurally valid, active, effective,
and released with capability `qualification-plan-abandonment-v1`. A version without that
capability cannot authorize a registry mutation even when the implementation is installed. The
authorizing workflow family must equal the owning study's workflow family.

The plan identity is caller-selected, but the writer derives the experiment family, owning study
path, frozen study identities, and lifecycle status from the verified registry and canonical
workflow repository. A caller cannot substitute an owning study path or status.

## Canonical event

The only abandonment event is `historical_plan_abandoned`, with event identity
`historical-plan-abandoned:<plan-id>`. Its payload records:

- the plan and experiment-family identities;
- the owning study path plus preregistration, plan, candidate-freeze, qualification-specification,
  and owning workflow-release SHA-256 identities copied from the frozen plan;
- the canonical owning study workflow, version, path, and terminal `cancelled` status;
- the exact active authorizing workflow path, version, release SHA-256, and capability;
- current canonical UTC time, stable human approver, concrete reason, and the prior registry event
  count and head hash.

The append occurs atomically under the existing qualification-registry lock and participates in
the existing hash chain and private head checkpoint. Evidence snapshots replay the event through
the same authoritative registry validator.

## Eligibility and terminal behavior

Abandonment is permitted only when all of the following are true:

1. the exact plan exists and contains a complete frozen study identity;
2. the canonical owning study still resolves to that exact path and workflow identity;
3. the owning study status is exactly `cancelled`;
4. the plan has neither a `historical_screen` nor a prior `historical_plan_abandoned` event; and
5. current human approval, reason, authorizing release, registry head, and event identity are valid.

Either `historical_screen` or `historical_plan_abandoned` closes a plan for the single-open-plan
invariant. Cancellation of a study without the registry event does not close its plan.

An abandoned plan cannot later receive a screen, Shadow registration, replay attachment, second
abandonment, revival, disposition, or terminal Evaluation evidence. Abandonment is an
administrative fact only: it is not `pass`, `fail`, `insufficient-evidence`, or `indeterminate`, and
it grants no prospective or operational authority.

## Compatibility

Registries containing only the earlier event vocabulary remain valid. Existing plans remain open
until a canonical abandonment or screen event is appended. Released v009 workflow bytes and all
existing registry and study evidence remain unchanged; the new capability first belongs to a
separately accepted, released, and activated successor workflow.
