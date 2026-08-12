# Impact

## Rules and artifacts affected

- Next workflow version metadata, `WORKFLOW.md` reproducibility/evidence requirements, and its
  generated `RELEASE.json` dependency digests.
- Workflow-native definition capture and formal execution tests may need extension so the new
  orchestration-source requirement is executable rather than documentary.
- No released v001 workflow/policy artifact, legacy experiment identity, result, or study is
  modified.

## Existing studies and hypotheses

- `strategy-forward-replication-research@v001/S001`: `continue-on-v001`. It is already completed
  with outcome `fail`; its exact immutable data, definitions, raw results, gate calculation,
  evidence, and independent conclusion remain authoritative. The dependency-role mismatch cannot
  change its Development gate because those failures were independently recomputed from frozen
  observations.
- No unfinished v001 studies exist at proposal time. New studies should use v002 only after an
  approved v002 release reaches the canonical branch; until then v001 remains active.

## Compatibility and migration risk

Pinning additional normative documents intentionally makes later edits require a new workflow
version. Capturing more orchestration source increases snapshot size and may change new semantic
fingerprints, but it must not mutate existing trial identities. Implementations must preserve
provider-free replay and avoid incorporating mutable paths without exact bytes or checksums.
