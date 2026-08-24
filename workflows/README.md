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
        status: superseded
        status_changed_at: '2026-08-13T07:34:39.412209Z'
        status_changed_by: ochowei@gmail.com
      v005:
        path: strategy-forward-replication-research--v005
        status: superseded
        status_changed_at: '2026-08-13T10:36:37.246256Z'
        status_changed_by: ochowei@gmail.com
      v006:
        path: strategy-forward-replication-research--v006
        status: superseded
        status_changed_at: '2026-08-14T06:36:20.963928Z'
        status_changed_by: ochowei@gmail.com
      v007:
        path: strategy-forward-replication-research--v007
        status: superseded
        status_changed_at: '2026-08-16T15:38:20.431520Z'
        status_changed_by: ochowei@gmail.com
      v008:
        path: strategy-forward-replication-research--v008
        status: active
        status_changed_at: '2026-08-16T15:38:20.431520Z'
        status_changed_by: ochowei@gmail.com
---
# Research Workflows

This directory is the canonical registry for versioned, human-and-Agent research workflow
contracts. A workflow version becomes effective only after its prepared release commit is merged
into the repository's canonical branch.

Use `trading-author-workflow` to review, create, or evolve a workflow,
`trading-operate-workflow` to run a pinned study, and `trading-evaluate-study` for independent
study conclusions. For authoring, preview a closed request with `trading workflow create --request
<path> --dry-run`, `trading workflow change create --request <path> --dry-run`, or `trading workflow
evolve --request <path> --dry-run`; after human confirmation, apply the same request without
`--dry-run`. These commands retain request and source files. Any exact-path move, pointer
replacement, or removal requires a separate human confirmation.

Use `uv run trading workflow validate --all` for deterministic validation. Low-level sync and
lifecycle transitions remain compatibility/diagnostic tools; guarded decisions and release
preparation remain separate human-authority steps. A prepared release has no authority until its
commit is merged into the canonical branch.

<!-- GENERATED:WORKFLOW_INDEX_START -->
| Workflow | Version | Status | Path |
| --- | --- | --- | --- |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v001` | `superseded` | [strategy-forward-replication-research--v001](strategy-forward-replication-research--v001/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v002` | `superseded` | [strategy-forward-replication-research--v002](strategy-forward-replication-research--v002/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v003` | `superseded` | [strategy-forward-replication-research--v003](strategy-forward-replication-research--v003/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v004` | `superseded` | [strategy-forward-replication-research--v004](strategy-forward-replication-research--v004/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v005` | `superseded` | [strategy-forward-replication-research--v005](strategy-forward-replication-research--v005/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v006` | `superseded` | [strategy-forward-replication-research--v006](strategy-forward-replication-research--v006/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v007` | `superseded` | [strategy-forward-replication-research--v007](strategy-forward-replication-research--v007/) |
| 策略前瞻驗證流程 (`strategy-forward-replication-research`) | `v008` | `active` | [strategy-forward-replication-research--v008](strategy-forward-replication-research--v008/) |
<!-- GENERATED:WORKFLOW_INDEX_END -->
