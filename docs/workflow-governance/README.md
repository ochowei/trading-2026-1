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
  predecessor-to-successor identity handoff; A1-2 Overview plus A1-2A identity formation, A1-2B
  release/activation authority, A1-2C active-version governance, and a separate family activation
  profile; and the independent A1-3 per-study lifecycle inside L3.
- [Workflow governance flow](workflow-governance-flow.html): B1 high-level role-handoff sequence.

## Diagram scope and review conclusion

- Last reviewed: 2026-08-29.
- A1 is the process-and-exception view of one exact Workflow version and the cross-identity handoff
  that creates a prospective successor. An active predecessor never returns to Draft; it remains
  immutable and active until successor activation changes it to `superseded`.
- A1-2 is one per-exact-version control-state model presented as an Overview and three segmented
  views: A (L1 successor identity formation), B (L2 release/activation authority), and C (L3
  active-version governance). Repeated N02 and N04 nodes are shared boundaries for the same
  canonical identities, not duplicate states or separate FSMs. Mutual exclusion is scoped to one
  immutable `workflows/<slug>--vNNN` identity, not the family: a family may contain one active
  predecessor and one draft or prepared successor at the same time. N01 is a prospective-successor
  entry boundary before an exact version identity exists; it is not a persisted registered-version
  state. Individual Sxxx lifecycle states remain outside this model.
- A1-2 keeps family activation policy outside the FSM. The generic required-path predicate is
  `exact version >= family.activation_required_from`; pre-boundary bootstrap is an explicit legacy
  exception. For `strategy-forward-replication-research`, v009 remains the final bootstrap version
  and v010+ requires explicit activation.
- `RELEASE.json` identifies a prepared release; for activation-enabled versions, only a valid
  version-root `ACTIVATION.json` bound to that release can establish the active control state.
- A1-3 is the canonical lifecycle view for one Sxxx inside one exact active version's L3. That
  version may coordinate 0..n independent A1-3 instances; their states do not become
  workflow-version control states.
- A prepared successor can coexist with its active predecessor, but the family-level prepared
  guard blocks creating, preregistering, starting, resuming, or freezing new outcome-relevant work
  while activation is pending.
- Study safety gates release preparation and activation, not the authoring handoff that creates a
  prospective input or exact draft successor. A release-safety failure switches control to the
  active predecessor while the same successor remains draft, then returns to that same draft for a
  fresh release check after safety closure.
- Repository facts do not yet persist a prospective successor identity for N01 or a canonical
  open/closed safety-assessment fact for N06 versus N04/N05. A future exact-version CLI must report
  `invalid` or `indeterminate` when those required facts are absent rather than infer them from
  prose or study counts.
- B1 is a high-level actor handoff summary. It is not a complete authority or lifecycle model; use
  A1 for the detailed gates and control states.
- A1 replaces the former B2 activity view. B2 was removed because it duplicated the primary
  flow while showing only a happy path. This scope correction closes the final GD-005 finding; the
  previously tracked GD-001 through GD-006 findings are resolved by diagram content or an explicit
  scope boundary.

The diagrams are explanatory views. When a diagram differs from canonical authority, follow the
registry, the exact released workflow, the shared study-governance rule, and the applicable skill.
