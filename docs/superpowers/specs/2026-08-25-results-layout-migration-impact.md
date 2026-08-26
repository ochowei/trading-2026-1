# Results Layout Migration Impact

## Classification

This is a behavior-affecting normative dependency and evidence-retention-boundary change. It
requires an accepted workflow change and a replacement workflow version; it is not a documentation
correction. Released workflow and completed-study bytes remain immutable.

## Existing workflow versions and studies

- Versions v001-v007 are superseded. Their completed, cancelled, or paused studies keep their exact
  historical artifacts and resolve moved paths only through the tracked digest-bound migration
  registry.
- Version v008 is active. S001 and S002 are completed and remain unchanged.
- v008/S003 was moved from `running` to `paused` by
  `codex-primary-researcher-fxi-mean-reversion` with reason
  `repository results path migration` before any artifact move.

## Proposed paused-study decision

`continue-on-v008` is recommended for v008/S003 after migration validation. The storage migration
does not change its frozen research design or outcomes. Resumption remains a separate guarded study
operation and is allowed only if all exact old paths resolve to byte-identical destinations, the
candidate-freeze and registry identities still validate, and v008 remains legally operable under
the final version-impact decision.

If any identity, digest, replay, or path-resolution invariant fails, S003 remains paused. The
migration must be repaired without replacing evidence; if exact evidence cannot be restored, the
impact decision must change to `close-invalidated` or a successor must use `restart-on-v009`.

## Risks and mitigations

| Risk | Required mitigation |
| --- | --- |
| Frozen path no longer exists | Resolve only through the tracked one-hop mapping and exact digest. |
| Artifact silently replaced | Verify pre/post bytes and reject digest drift. |
| Completed study rewritten | Never edit frozen study artifacts; compatibility lives in shared resolution code. |
| New output returns to the flat layout | Change every canonical writer and test its destination. |
| GC drops a moved artifact | Treat both mapping entries and destination paths as references. |
| Migration registry becomes mutable authority | Append-only schema, deterministic validation, no caller-supplied substitution. |
| Active research changes during migration | Keep S003 paused until all validation and a separate resume decision. |

## Version boundary

The replacement workflow must specify the categorized evidence namespaces and the exact migration
compatibility contract. The active v008 release remains authoritative until an approved replacement
release is merged. Creating a draft does not authorize migration execution, study execution,
qualification, outcome inspection, broker access, or trading.
