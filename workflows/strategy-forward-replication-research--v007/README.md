---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v007
definition: WORKFLOW.md
supersedes: v006
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v006/work/changes/retrospective-selection-boundary-screen-compatibility--c001
policies:
- family: us-equity-market
  version: v002
  path: policies/us-equity-market--v002
  release_digest: 9c4feb8ec5bea92f0df9c30f31ea9553b4ef338b7740fcfbecb72cc1090d5978
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
- path: docs/auxiliary-unavailable-decision-reproducibility.md
  role: normative
- path: docs/result-validity-and-trial-history-v005.md
  role: normative
- path: docs/canonical-sleeve-execution.md
  role: normative
- path: docs/historical-qualification-and-shadow-v007.md
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

本 draft 完整保留 v006 的 retrospective、clean Historical、Shadow、activation、monitoring、
policy、auxiliary availability 與 observation-provenance guards，並納入 accepted change
`strategy-forward-replication-research@v006/C001`。新增共同 frozen selection boundary 語義，
要求 forward epoch 與 retrospective checkpoint 在 registration、screen coordination 與
family-wise adjustment 間一致；並要求 provider-free end-to-end release validation。這不改變
任何 gate、trial family、既有 study 或 promotion authority。

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

| ID | Title | Status | Released in | Path |
| --- | --- | --- | --- | --- |
| `C001` | Frozen Historical Plan Preservation and Readiness | `accepted` | `-` | [frozen-historical-plan-readiness--c001](work/changes/frozen-historical-plan-readiness--c001/) |
| `C002` | Study-Time Retrospective Evaluation | `accepted` | `-` | [study-time-retrospective-evaluation--c002](work/changes/study-time-retrospective-evaluation--c002/) |
<!-- GENERATED:WORK_INDEX_END -->
