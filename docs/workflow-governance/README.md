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

- [Workflow governance layers](workflow-governance-layers.html): A1 single-Workflow inter-layer
  governance flow, the equivalent A1-2 workflow control state machine, and the separate A1-3
  per-study lifecycle inside L3.
- [Workflow governance flow](workflow-governance-flow.html): B1 high-level role-handoff sequence.

## Diagram scope and review conclusion

- Last reviewed: 2026-08-28.
- A1 is the process-and-exception view of one Workflow moving exclusively between L1, L2, and L3;
  the Workflow occupies only one layer at a time.
- A1-2 is the equivalent finite-state-machine view of that same single-Workflow governance model.
  It does not define a second process or mix individual study lifecycle states into Workflow
  control state.
- A1-3 is the canonical lifecycle view for one Sxxx inside L3. A Workflow in L3 may coordinate
  0..n independent A1-3 instances without ceasing to occupy only L3.
- B1 is a high-level actor handoff summary. It is not a complete authority or lifecycle model; use
  A1 for the detailed gates and control states.
- A1 replaces the former B2 activity view. B2 was removed because it duplicated the primary
  flow while showing only a happy path. This scope correction closes the final GD-005 finding; the
  previously tracked GD-001 through GD-006 findings are resolved by diagram content or an explicit
  scope boundary.

The diagrams are explanatory views. When a diagram differs from canonical authority, follow the
registry, the exact released workflow, the shared study-governance rule, and the applicable skill.
