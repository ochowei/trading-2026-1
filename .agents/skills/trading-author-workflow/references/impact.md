# Workflow Version Impact

Read `.agents/rules/workflow-study-governance.md` for the canonical study lifecycle and authority
boundary. This reference covers only what workflow authors must decide at a version boundary.

## When a new version is required

Use an accepted change and replacement version for changes to purpose, scope, stages, transitions,
authority, data roles, trial/selection rules, evidence requirements, outcome semantics,
pause/recovery/termination, policy adoption, or normative dependency behavior. Do not label a
behavior-changing edit as documentation-only.

Individual strategy parameters, signals, data dependencies, or execution definitions normally
create new workflow-native trials when the released workflow rules themselves remain unchanged.

## Existing studies

Read studies only to assess impact; do not execute, repair, migrate, complete, or reinterpret them.
Before an active version is superseded or retired, every unfinished study must be `paused`,
`completed`, or `cancelled`. A running, preregistered, draft, or awaiting-review study blocks the
version boundary until it reaches a legal safe state through the study operator/reviewer.

For each paused study affected by a replacement or retirement, record one explicit impact decision:

- `continue-on-vNNN`;
- `restart-on-vNNN`; or
- `close-invalidated`.

This MVP records and reviews the decision in change impact material; it does not add a new
consumption state machine. Never move or overwrite an old study. A continued or restarted effort
creates the next CLI-allocated local study under the target version and records the exact old study
in `revisits`.

Study IDs are local to each exact workflow version. Do not carry an `Sxxx` across versions or infer
family-wide numbering. A replacement version with no studies starts at its own `S001`.

## Shared dependencies

Changing a normative dependency or selected policy in a way that affects the active workflow
requires an accepted change and new release; never rewrite the active release's pinned digest.
Reference-only changes do not redefine workflow behavior unless the reference is explicitly pinned
for release stability.
