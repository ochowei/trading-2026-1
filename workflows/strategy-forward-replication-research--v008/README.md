---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v008
definition: WORKFLOW.md
supersedes: v007
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v007/work/changes/frozen-historical-plan-readiness--c001
- workflows/strategy-forward-replication-research--v007/work/changes/study-time-retrospective-evaluation--c002
capabilities:
- study-time-retrospective-v1
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
- path: docs/controlled-followup-cutover.md
  role: normative
- path: docs/live-drift-and-recovery.md
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

本版本完整保留 v007 的 retrospective-confirmatory、clean Historical、Shadow、activation、
monitoring、policy、auxiliary availability 與 observation-provenance guards，並合併兩個由
`ochowei@gmail.com` 接受的 source changes：

- `strategy-forward-replication-research@v007/C001`：加入 explicit clean-Historical calendar、
  complete-family register-only readiness、recoverable logical transaction，以及 pinned pre-freeze
  evidence preservation；
- `strategy-forward-replication-research@v007/C002`：加入 `study-time-retrospective` route，使 study
  可使用當下既有歷史資料完成 Development 與 time-ordered retrospective Evaluation，但永不
  因此取得 Shadow、activation 或 live authority。

完整行為規則都在 `WORKFLOW.md`。同目錄的 `STAGES_AND_OUTCOMES.md` 同時提供精簡白話版與
完整版解說，是 release 時固定 bytes 的 reference companion，不是第二份 normative authority。

本版本的 authority 永遠只由 root `workflows/README.md` lifecycle registry 決定：draft 不具
執行權，active 時才可建立新 study，superseded／retired 後不得建立新 study。Version bytes
本身不建立或操作 study，也不授權 v004/S004 registration、resume、Historical access 或其他
outcome-relevant work。

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
