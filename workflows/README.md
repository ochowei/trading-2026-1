---
schema_version: 1
workflows:
  strategy-forward-replication-research:
    title: 策略前瞻驗證流程
    versions:
      v001:
        path: strategy-forward-replication-research--v001
        status: draft
        status_changed_at: null
        status_changed_by: null
---
# Research Workflows

This directory is the canonical registry for versioned, human-and-Agent research workflow
contracts. A workflow version becomes effective only after its prepared release commit is merged
into the repository's canonical branch.

Use `trading-author-workflow` to review, create, or evolve a workflow,
`trading-operate-workflow` to run a pinned study, and `trading-evaluate-study` for independent
study conclusions. Use `uv run trading workflow validate --all` for deterministic validation and
`uv run trading workflow sync` to rebuild generated indexes.

<!-- GENERATED:WORKFLOW_INDEX_START -->
| Workflow | Version | Status | Path |
| --- | --- | --- | --- |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v001` | `draft` | [strategy-forward-replication-research--v001](strategy-forward-replication-research--v001/) |
<!-- GENERATED:WORKFLOW_INDEX_END -->
