# Workflow Release-Safety Persistence Impact

## Rules and artifacts affected

This changes workflow release-safety evidence, family-level action eligibility, release readiness,
and validation. It requires an accepted change and v009 contract update. It adds a repeated tracked
artifact pattern under a draft successor and guarded `workflow safety assess/clear` commands.

It does not change study lifecycle states, study outcomes, release/activation authority, v009
bootstrap, the v010 explicit activation boundary, broker access, order authority, or the identity of
any existing workflow version or study.

## Existing studies and hypotheses

- v008/S001 and v008/S002 remain completed and immutable.
- v008/S003 remains paused and pinned to v008. Its impact disposition remains `continue-on-v008`,
  consistent with the accepted v008 C001/C002 material. This change neither resumes nor modifies it.
- A later real assessment that lists S003 must still record a guarded clearance resolution and exact
  evidence; this change does not manufacture that operational event.
- No study is created, transitioned, executed, evaluated, migrated, or reinterpreted by this change.

## Compatibility and migration risk

Existing versions without `work/release-safety/` remain valid. The new validator is additive and
examines safety artifacts only when the directory exists. Existing prepared-successor guards remain
unchanged; an open safety assessment adds another fail-closed family guard.

Main risks are hand-authored identity, mutable timestamps, duplicate open assessments, clearing an
unsafe study, stale evidence digests, or treating absent persistence as proof. Guarded writers derive
canonical fields, publish add-only files under the authoring lock, and full validation rejects each
of those cases. The separate state-query CLI remains deferred.
