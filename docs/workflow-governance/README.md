# Workflow Governance Documentation

This directory is the human-facing entry point for workflow-governance diagrams and their scope.
It does not replace lifecycle, study-authority, workflow-contract, or skill authority.

## Canonical authority

- [Workflow lifecycle registry](../../workflows/README.md): version registration and lifecycle
  status, family activation boundary, release preparation, and immutable Workflow Release
  Activation evidence.
- [Workflow study governance](../../.agents/rules/workflow-study-governance.md): shared study
  identity, lifecycle, stage-specific authority, operator/reviewer separation, evidence, privacy,
  and version-boundary rules.

The exact released `WORKFLOW.md` pinned by a study remains the procedure authority for that study.

## Workflow skills

- [Author workflows](../../.agents/skills/trading-author-workflow/SKILL.md): create, evolve,
  abandon, retire, and prepare releases.
- [Operate studies](../../.agents/skills/trading-operate-workflow/SKILL.md): create, preregister,
  execute, pause, cancel, and submit studies for review.
- [Evaluate studies](../../.agents/skills/trading-evaluate-study/SKILL.md): independently assess
  frozen evidence and prepare terminal outcomes.

## Diagrams

- [Workflow governance layers](workflow-governance-layers.html): A1 exact-version governance and
  predecessor-to-successor identity handoff, the equivalent A1-2 per-exact-version control-state
  view, and the separate A1-3 per-study lifecycle inside L3.
- [Workflow governance flow](workflow-governance-flow.html): B1 high-level role-handoff sequence.

## Diagram scope and review conclusion

- Last reviewed: 2026-08-28.
- A1 is the process-and-exception view of one exact Workflow version and the cross-identity handoff
  that creates a prospective successor. An active predecessor never returns to Draft; it remains
  immutable and active until successor activation changes it to `superseded`.
- A1-2 is the equivalent per-exact-version control-state view. Mutual exclusion is scoped to one
  immutable `workflows/<slug>--vNNN` identity, not the family: a family may contain one active
  predecessor and one draft or prepared successor at the same time. N01 is a prospective-successor
  entry boundary before an exact version identity exists; it is not a persisted registered-version
  state. Individual Sxxx lifecycle states remain outside this model.
- `RELEASE.json` identifies a prepared release; for activation-enabled versions, only a valid
  version-root `ACTIVATION.json` bound to that release can establish the active control state.
- A1-3 is the canonical lifecycle view for one Sxxx inside one exact active version's L3. That
  version may coordinate 0..n independent A1-3 instances; their states do not become
  workflow-version control states.
- A prepared successor can coexist with its active predecessor, but the family-level prepared
  guard blocks creating, preregistering, starting, resuming, or freezing new outcome-relevant work
  while activation is pending.
- Repository facts do not yet persist a prospective successor identity for N01 or a canonical
  safety-required intent for N06. A future exact-version CLI must report `invalid` or
  `indeterminate` when those required facts are absent rather than infer them from prose.
- B1 is a high-level actor handoff summary. It is not a complete authority or lifecycle model; use
  A1 for the detailed gates and control states.
- A1 replaces the former B2 activity view. B2 was removed because it duplicated the primary
  flow while showing only a happy path. This scope correction closes the final GD-005 finding; the
  previously tracked GD-001 through GD-006 findings are resolved by diagram content or an explicit
  scope boundary.

The diagrams are explanatory views. When a diagram differs from canonical authority, follow the
registry, the exact released workflow, the shared study-governance rule, and the applicable skill.
