---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v006
definition: WORKFLOW.md
supersedes: v005
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v005/work/changes/explicit-retrospective-role-calendar--c001
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
- path: docs/historical-qualification-and-shadow-v006.md
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

本 draft 完整保留 v005 的 retrospective、clean Historical、Shadow、activation、monitoring、
policy、auxiliary availability 與 observation-provenance guards，並納入 accepted change
`strategy-forward-replication-research@v005/C001`。新增 explicit retrospective role calendar，
使 completed Development context 可位於 retrospective evaluation 之後，同時將 warmup-only、
Development 與 Evaluation sessions 分別凍結且禁止重疊。這不改變任何 gate 或 promotion
authority。

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
