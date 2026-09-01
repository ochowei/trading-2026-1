---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v009
definition: WORKFLOW.md
supersedes: v008
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v008/work/changes/categorized-results-layout-migration--c002
- workflows/strategy-forward-replication-research--v008/work/changes/fixed-calendar-retrospective-protocol--c005
- workflows/strategy-forward-replication-research--v008/work/changes/guarded-challenge-only-execution--c001
- workflows/strategy-forward-replication-research--v008/work/changes/workflow-release-activation--c003
- workflows/strategy-forward-replication-research--v008/work/changes/workflow-release-safety-persistence--c004
capabilities:
- fixed-calendar-retrospective-v1
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
- path: docs/result-storage-layout-v009.md
  role: normative
- path: docs/controlled-followup-cutover.md
  role: reference
- path: docs/live-drift-and-recovery.md
  role: reference
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

本 v009 draft 是 v008 的自包含接替版。它保留 v006/S001 的 selection-boundary 教訓，以及 v007 已發布的 complete-family registration、evidence preservation 與 fail-closed retrospective 基線。

直接 source changes 為 accepted v008/C001-C005：C001 guarded challenge-only execution；C002 categorized result-layout migration；C003 immutable Workflow Release Activation；C004 guarded workflow release-safety persistence；C005 fixed-calendar retrospective protocol。C005 將 study scope 固定為 2013 warmup、2014-2018 Development、2019 quarantine、2020-2024 Historical Evaluation 與 2025 retrospective execution replay，並移除 prospective Shadow、Controlled Activation、Active monitoring 及所有 promotion/live authority。

Combined impact review 維持 v008/S001、v008/S002 completed bytes/outcomes 不變；paused v008/S003 繼續依 accepted continue-on-v008，不搬移、不重解、不恢復。Accepted changes 本身不是 implementation 或 release evidence；C001-C005 的 compiler、guards、migration、replay、atomic publication、compatibility 與 provider-free release tests 已另於 post-acceptance validation evidence 實作並驗證。v009 仍是 draft，這些證據不構成 release、activation 或 study authority；Workflow-version v009 bootstrap 與 v010 起 explicit release activation boundary 保持不變。

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

| ID | Title | Status | Outcome | Path |
| --- | --- | --- | --- | --- |
| `S001` | FXI No-ClosePos ATR-Floor Mean-Reversion Fixed-Calendar Retrospective Study | `completed` | `fail` | [fxi-no-closepos-atr-floor-mean-reversion-fixed-calendar-retrospective--s001](work/studies/fxi-no-closepos-atr-floor-mean-reversion-fixed-calendar-retrospective--s001/) |

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
