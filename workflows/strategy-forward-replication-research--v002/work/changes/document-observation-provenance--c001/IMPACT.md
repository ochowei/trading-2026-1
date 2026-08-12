# Impact

## Rules and artifacts affected

The replacement version will clarify the Required artifacts/evidence and implementation-link
sections of `WORKFLOW.md`, and will update `docs/reproducibility.md` plus
`docs/result-validity-and-trial-history.md`. It will preserve the v002 purpose, stages, trial
counting, candidate selection, Development/Historical/Shadow roles, gates, outcome semantics,
policy pins, pause/recovery rules, legacy inventory protection, and broker authorization boundary.

The implementation introduced by PR #169 is the reference behavior to document. No result,
snapshot, trial-registry event, study artifact, released policy, or legacy experiment identity will
be migrated or rewritten by this change.

## Existing studies and hypotheses

All v002 studies are already terminal:

- S001 is `cancelled` because its required history start preceded ACWI availability;
- S002 is `completed` with `indeterminate` outcome;
- S003 is `completed` with `fail` outcome.

There are no unfinished studies requiring `continue-on-v003`, `restart-on-v003`, or
`close-invalidated`. Existing hypotheses, preregistrations, evidence, conclusions, completion
identities, and outcomes remain pinned to v002 and unchanged. A future study may be created under
v003 only after v003 becomes effective on the canonical branch and receives its own explicit topic
and preregistration approvals.

## Compatibility and migration risk

The change is backward compatible for readers because it documents an additive metadata field
already used by workflow-native execution. Legacy and ordinary experiment results must not receive
synthetic workflow provenance. The principal governance risk is an invalid intermediate state if a
shared normative document changes while v002 is still active; therefore the documentation edits,
v003 release preparation, and v002 supersession must remain one validated release change.

No raw private data enters `workflows/`. Historical result JSON remains subject to the existing
ignored/local-only boundary, and tracked evidence stores only exact references and checksums.
