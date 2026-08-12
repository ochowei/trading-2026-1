---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v002
definition: WORKFLOW.md
supersedes: v001
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v001/work/changes/pin-normative-dependencies--c001
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
  role: normative
- path: docs/reproducibility.md
  role: normative
- path: docs/result-validity-and-trial-history.md
  role: normative
- path: docs/canonical-sleeve-execution.md
  role: normative
- path: docs/historical-qualification-and-shadow.md
  role: normative
- path: docs/controlled-followup-cutover.md
  role: normative
- path: docs/live-drift-and-recovery.md
  role: normative
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

本版完整保留 v001 的研究 stages、gates、authority boundaries、policy pins 與 legacy
protections，並實作 accepted change
`strategy-forward-replication-research@v001/C001`。該 change 來自 S001 end-to-end pilot 的
獨立 review：修正 `WORKFLOW.md` 與 release metadata 對四個 normative dependencies 的角色
不一致，並要求 formal observation 固定完整 outcome-relevant orchestration source identity。

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
