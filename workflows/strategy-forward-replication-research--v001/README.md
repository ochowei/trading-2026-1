---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v001
definition: WORKFLOW.md
supersedes: null
derived_from: null
source_changes: []
policies:
- family: us-equity-market
  version: v001
  path: policies/us-equity-market--v001
  release_digest: 7df1e266aa72ccfaca3efa3e490ad6234f300bb0bfc4e31b3dd3c85ab93de542
- family: firstrade-manual-trading
  version: v001
  path: policies/firstrade-manual-trading--v001
  release_digest: 0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9
- family: canonical-execution
  version: v001
  path: policies/canonical-execution--v001
  release_digest: e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925
- family: portfolio-risk
  version: v001
  path: policies/portfolio-risk--v001
  release_digest: 63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69
dependencies:
- path: .agents/rules/execution-model.md
  role: reference
- path: docs/reproducibility.md
  role: normative
- path: docs/result-validity-and-trial-history.md
  role: normative
- path: docs/canonical-sleeve-execution.md
  role: reference
- path: docs/historical-qualification-and-shadow.md
  role: normative
- path: docs/controlled-followup-cutover.md
  role: reference
- path: docs/live-drift-and-recovery.md
  role: reference
- path: docs/market-data.md
  role: reference
- path: docs/manual-execution-ledger.md
  role: reference
- path: docs/strategy-forward-replication-research-workflow.md
  role: reference
---
# 策略前瞻驗證流程

This directory contains a self-contained workflow contract. Its lifecycle state is authoritative
only in the root `workflows/README.md` registry.

## Authoring basis

本版採 document-led creation，由
`docs/strategy-forward-replication-research-workflow.md` 匯入。來源最後變更於 commit
`1399e19a3eae118615d2318fd1c74cb3ea55aa8c`，匯入時 SHA-256 為
`7714059846fb42a6c24760db84589b36d97dea026b12ed7fd6c860e255112660`。

已確認的 authoring 決策包括：使用固定 slug `strategy-forward-replication-research`；研究與
晉級需由具穩定識別碼的人類負責人核准；來源所列門檻是不可放寬的 floor；每輪研究預註冊
有限的 `maximum_trials`；唯一候選只依 Development 的完整有效候選集合與 canonical
base-net daily-equity Sharpe 選出。Repository 現行較嚴格的 reproducibility、selection
adjustment、Historical、Shadow、cutover 與 drift 規則一併納入。

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
