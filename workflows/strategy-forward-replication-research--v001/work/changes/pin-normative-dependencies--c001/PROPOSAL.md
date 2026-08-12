# Proposal

## Current problem

`WORKFLOW.md` classifies `.agents/rules/execution-model.md`,
`docs/canonical-sleeve-execution.md`, `docs/controlled-followup-cutover.md`, and
`docs/live-drift-and-recovery.md` as normative. The released version metadata and `RELEASE.json`
instead classify those paths as references, so their exact SHA-256 values are not release-pinned.
The workflow's declared semantic authority therefore exceeds its immutable release dependency set.

The S001 pilot also showed that an immutable Research Definition Snapshot captured strategy,
detector, backtester, resolved configuration, dependency versions, costs, policies, and data but
did not capture every maintained orchestration source used to bind a released workflow and execute
the formal observation. S001 remained independently reproducible from its raw immutable results,
but the boundary should be explicit and mechanically enforced for later studies.

## Proposed workflow change

Create a self-contained `v002` that:

1. classifies the four paths above as normative in version metadata so release preparation pins
   their exact SHA-256 values consistently with `WORKFLOW.md`;
2. requires formal observations to capture or independently checksum every outcome-relevant
   maintained orchestration source, including workflow/policy resolution and workflow-native run
   coordination, and record those identities in study evidence;
3. treats a missing or drifting orchestration identity as `indeterminate` until repaired without
   changing frozen research semantics; and
4. preserves all v001 research gates, lifecycle boundaries, policy pins, and legacy protections.

## Expected effect

The replacement release will have one unambiguous normative dependency set and a complete formal
source-identity boundary. Existing v001 artifacts and completed studies remain immutable and
reproducible; no result, threshold, policy, strategy, or study outcome is rewritten.
