# Proposal

## Current problem

The v002 workflow requires every workflow-native formal observation to preserve exact
outcome-relevant orchestration identity. PR #169 implements this as the persisted
`metadata.observation_provenance` result field, including canonical argv, workflow release and
definition hashes, composite policy-set identity, complete Git HEAD, and exact maintained
orchestration source bytes.

The shared normative documents `docs/reproducibility.md` and
`docs/result-validity-and-trial-history.md` do not yet describe this wire contract. Editing either
document while v002 remains active would invalidate its pinned release digest, so the documentation
cannot lawfully be corrected in place.

## Proposed workflow change

Create `strategy-forward-replication-research@v003` as the complete replacement for v002. Preserve
all research stages, roles, gates, policies, outcomes, safety boundaries, and study semantics.
Clarify only the formal-observation contract and its authoritative storage boundary:

- workflow-native result metadata records `metadata.observation_provenance` before strategy output
  inspection;
- canonical argv identifies the exact research identity, workflow path, manifest path, and run
  mode;
- workflow evidence pins family, version, path, `RELEASE.json` SHA-256, `WORKFLOW.md` SHA-256, and
  composite policy-set identity;
- orchestration evidence pins complete Git HEAD plus exact UTF-8 source bytes and SHA-256 identities
  for every maintained source that determines workflow binding or formal publication;
- missing or unreadable identities fail closed before a formal result is published;
- historical result JSON remains local-only unless repository policy explicitly retains it, while
  tracked manifests, trial-registry observations, and study evidence retain exact paths and
  checksums.

Update the two shared normative documents to describe the same contract, then let the v003 release
pin their new SHA-256 values. Keep the same four released policy selections.

## Expected effect

The workflow contract, implementation, architecture map, reproducibility documentation, and result
documentation will describe one consistent provenance boundary. Existing v002 studies and their
terminal outcomes remain immutable. The change adds no research discretion, relaxes no gate, and
grants no broker, activation, or live-trading authority.
