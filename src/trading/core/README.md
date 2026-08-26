# `trading.core` ownership map

This namespace is mixed for compatibility and must not be interpreted as "all current" or "all
legacy." Canonical ownership is determined by `docs/ARCHITECTURE.md` and the executable path
classification under `config/repository-checks/`.

## Maintained shared infrastructure

Accounting, market-independent qualification values, sleeve evaluation, ledger, reconciliation,
proposal, followup lifecycle, drift, and policy-authoring modules remain maintained infrastructure.
Some exact implementation paths are pinned by released policies and must not be moved or rewritten
without a successor policy release.

## Legacy strategy compatibility

The `base_*`, execution-strategy, bundle-strategy, and data-fetcher seams preserve historical
strategy and migration behavior. New workflow-native research definitions must use
`trading.research_definitions` and its maintained primitives rather than treating these files as a
new experiment framework.

`results`, `evaluation`, `definition_resolver`, `sync_docs`, `performance_analyzer`, and
`legacy_experiments` are historical import aliases whose canonical implementations live under
`trading.legacy`.

## Workflow import compatibility

`workflow_authoring`, `workflow_studies`, `study_qualification`, `study_terminal_evidence`, and
`qualification_workflow` preserve historical imports. Their canonical implementations live under
`trading.workflow`. Keep the alias modules thin and place new workflow runtime behavior in the
canonical namespace.
