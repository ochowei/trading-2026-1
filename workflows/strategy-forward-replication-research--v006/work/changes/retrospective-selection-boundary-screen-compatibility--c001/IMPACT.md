# Impact

## Rules and artifacts affected

The change affects the workflow's selection-adjustment invariant, retrospective qualification
screen requirements, release-readiness evidence, and the normative Phase 6 qualification
contract. A complete implementation is expected to affect the family-wise adjustment evaluator
and focused domain, workflow, CLI, registry, and end-to-end regression tests.

It does not change strategy definitions, signals, execution policies, costs, evaluation roles,
folds, family membership, baseline identity, random or bootstrap seeds, numerical gates,
classification, outcome interpretation, or promotion boundaries. The released v006 workflow,
source hashes, completed studies, and registry events remain immutable. Because this clarifies and
enforces outcome-relevant screen behavior, acceptance requires a new workflow version rather than
an erratum.

## Existing studies and hypotheses

- There are no unfinished studies under v006 requiring `continue-on-vNNN`, `restart-on-vNNN`, or
  `close-invalidated` disposition.
- `strategy-forward-replication-research@v006/S001` is completed `indeterminate` and remains
  immutable. Its six observations and exposed 2010-2014 sessions cannot be rerun as confirmatory
  evidence after the verifier changes.
- The separate v004/S004 sealed 2027-2031 clean Historical plan remains unchanged. This change
  neither opens that evidence nor imports it into a replacement workflow.
- Any later research under the replacement version must use the next CLI-allocated local study
  identity. If it revisits an earlier study, it must record that exact path and independently
  satisfy preregistration and authorization requirements.

## Compatibility and migration risk

Forward plans must retain their current wire representation, plan IDs, timestamp field, and
selection-adjustment behavior. Retrospective plans must retain their distinct checkpoint type and
non-promotional boundary. Existing payloads that omit both boundaries remain valid only where the
current complete-history rules already allow them.

The main risks are silently treating retrospective evidence as forward-clean, accepting a trial
registered after the checkpoint, validating a different family universe or selected trial,
changing old serialization hashes, or adding a test that bypasses the production coordination
path. Compatibility tests must prove old payload round trips, while the new end-to-end test must
reach the actual selection-adjustment evaluator without provider or market-outcome access.
