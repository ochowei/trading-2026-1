# Legacy Experiment Retirement Workflow Contract Alignment Proposal

## Current problem

The repository has terminally retired the legacy experiment research system and moved its final
retained results byte-for-byte from `results/experiment-results/` to read-only `legacy/results/`.
The append-only path-migration registry now uses schema 2 and permits one digest-identical v010
retirement hop after an existing v009 categorized-result mapping, for a maximum of two hops.

The current v010 workflow draft was evolved only from accepted v009/C001 and still repeats the
v009 result-storage contract: it calls `results/experiment-results/` canonical and permits only a
single migration hop. That text conflicts with the canonical repository architecture, the v010
legacy-retirement contract, the tracked migration registry, and the maintained resolver. Structural
workflow validation cannot establish this semantic alignment by itself.

Released v009 bytes and their pinned dependency digests cannot be rewritten. The correction
therefore requires a separate accepted v009 workflow change and an updated complete v010
replacement contract.

## Proposed workflow change

Add the following narrowly scoped result-retirement rules to the v010 replacement workflow:

- Treat `legacy/results/<experiment>/` as the terminal read-only archive for every retained legacy
  experiment result class. `results/experiment-results/` is removed and must not be recreated.
- Preserve the existing v009 categorized-result contract as historical first-hop context, but add
  `docs/legacy-experiment-retirement-v010.md` as the normative successor for legacy-result
  retirement and path resolution. The successor overrides only the legacy-result namespace,
  retirement, and hop-limit rules; unchanged workflow-native namespaces and other v009 storage
  rules remain in force.
- Permit at most two append-only path-migration hops: a v009 historical path may resolve to the
  categorized path and then through exactly one v010 retirement mapping to `legacy/results/`.
  Every hop must preserve the original SHA-256. Reject longer chains, cycles, duplicate mappings,
  missing terminal bytes, unsafe paths, artifact-class conflicts, or digest drift.
- Keep released workflow, study, result, and registry bytes immutable. Historical references are
  resolved through the canonical migration registry rather than rewritten.
- Prohibit archived legacy results from becoming current result validity, selection, ranking,
  qualification, screen, terminal Evaluation, Shadow, Active, followup new-entry, broker, order,
  position, or live authority. Read-only archive diagnostics and fail-closed exit compatibility for
  already-owned positions do not restore research or trading authority.
- Leave workflow-native research definitions, trial artifacts, study evidence, content-addressed
  evidence, and registries in their current canonical namespaces.

The v010 authoring source, complete `WORKFLOW.md`, evolve request, dependency classification, and
combined impact statement must be updated together after this change receives an independent human
acceptance decision. v009 `WORKFLOW.md`, `RELEASE.json`, and pinned dependencies remain unchanged.

## Expected effect

The v010 release candidate will describe the repository that it actually governs, while frozen v009
and earlier evidence remains byte-identical and replayable. The change closes a documentation and
dependency gap only; it does not execute a study, inspect an outcome, mutate a qualification plan,
restore legacy execution, authorize promotion, or grant any operational or trading authority.
