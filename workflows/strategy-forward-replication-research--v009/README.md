---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v009
definition: WORKFLOW.md
supersedes: v008
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v008/work/changes/categorized-results-layout-migration--c002
- workflows/strategy-forward-replication-research--v008/work/changes/guarded-challenge-only-execution--c001
- workflows/strategy-forward-replication-research--v008/work/changes/workflow-release-activation--c003
- workflows/strategy-forward-replication-research--v008/work/changes/workflow-release-safety-persistence--c004
capabilities:
- study-time-retrospective-v1
- workflow-release-safety-v1
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
- path: docs/reproducibility-v008.md
  role: normative
- path: docs/auxiliary-unavailable-decision-reproducibility.md
  role: normative
- path: docs/result-validity-and-trial-history-v005.md
  role: normative
- path: docs/canonical-sleeve-execution.md
  role: normative
- path: docs/historical-qualification-and-shadow-v008.md
  role: normative
- path: docs/historical-qualification-and-shadow-v009.md
  role: normative
- path: docs/controlled-followup-cutover.md
  role: normative
- path: docs/live-drift-and-recovery.md
  role: normative
- path: docs/result-storage-layout-v009.md
  role: normative
- path: docs/market-data.md
  role: reference
- path: docs/manual-execution-ledger.md
  role: reference
- path: docs/research-evidence-preservation.md
  role: reference
- path: docs/strategy-forward-replication-research-workflow.md
  role: reference
- path: workflows/strategy-forward-replication-research--v008/STAGES_AND_OUTCOMES.md
  role: reference
  pinned: true
---
# 策略前瞻驗證流程

This directory contains a self-contained workflow contract. Its lifecycle state is authoritative
only in the root `workflows/README.md` registry.

## Authoring basis

Combine accepted v008/C001 guarded challenge-only execution, v008/C002 categorized result-layout migration, v008/C003 immutable Workflow Release Activation, and v008/C004 guarded workflow release-safety persistence. Preserve the v009 bootstrap and v010 explicit activation boundary; workflow-release-safety-v1 becomes effective only when v009 is active.

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
