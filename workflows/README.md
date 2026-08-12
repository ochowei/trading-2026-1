---
schema_version: 1
workflows:
  strategy-forward-replication-research:
    title: 策略前瞻驗證流程
    versions:
      v001:
        path: strategy-forward-replication-research--v001
        status: superseded
        status_changed_at: '2026-08-12T06:33:13.489428Z'
        status_changed_by: ochowei@gmail.com
      v002:
        path: strategy-forward-replication-research--v002
        status: superseded
        status_changed_at: '2026-08-12T12:41:21.866280Z'
        status_changed_by: ochowei@gmail.com
      v003:
        path: strategy-forward-replication-research--v003
        status: superseded
        status_changed_at: '2026-08-12T14:45:37.148770Z'
        status_changed_by: ochowei@gmail.com
      v004:
        path: strategy-forward-replication-research--v004
        status: active
        status_changed_at: '2026-08-12T14:45:37.148770Z'
        status_changed_by: ochowei@gmail.com
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
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v001` | `superseded` | [strategy-forward-replication-research--v001](strategy-forward-replication-research--v001/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v002` | `superseded` | [strategy-forward-replication-research--v002](strategy-forward-replication-research--v002/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v003` | `superseded` | [strategy-forward-replication-research--v003](strategy-forward-replication-research--v003/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v004` | `active` | [strategy-forward-replication-research--v004](strategy-forward-replication-research--v004/) |
<!-- GENERATED:WORKFLOW_INDEX_END -->
