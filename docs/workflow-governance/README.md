# Workflow Governance Documentation

This directory is the human-facing entry point for workflow-governance diagrams and their scope.
It does not replace lifecycle, study-authority, workflow-contract, or skill authority.

## Canonical authority

- [Workflow lifecycle registry](../../workflows/README.md): version registration and lifecycle
  status. A prepared release becomes effective only after its commit reaches the canonical branch.
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

- [Workflow governance layers](workflow-governance-layers.html): A1 inter-layer governance and A2
  internal-state reference.
- [Workflow governance flow](workflow-governance-flow.html): B1 high-level role-handoff sequence.

## Diagram scope and review conclusion

- Last reviewed: 2026-08-24.
- A1 is the cross-layer governance flow, including decisions, fail-closed guards, recovery, and
  handoffs between L1, L2, and L3.
- A2 is the internal-state reference for each Layer, including lifecycle alternatives and explicit
  authority boundaries.
- B1 is a high-level actor handoff summary. It is not a complete authority or lifecycle model; use
  A1 and A2 for the detailed gates and states.
- A1 and A2 replace the former B2 activity view. B2 was removed because it duplicated the primary
  flow while showing only a happy path. This scope correction closes the final GD-005 finding; the
  previously tracked GD-001 through GD-006 findings are resolved by diagram content or an explicit
  scope boundary.

The diagrams are explanatory views. When a diagram differs from canonical authority, follow the
registry, the exact released workflow, the shared study-governance rule, and the applicable skill.
