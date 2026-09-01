---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v011
definition: WORKFLOW.md
supersedes: v010
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v010/work/changes/shared-qualification-state-authority--c001
capabilities:
- fixed-calendar-retrospective-v1
- qualification-plan-abandonment-v1
- shared-qualification-state-v1
- cross-chain-plan-administration-v1
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
- path: docs/historical-qualification-and-shadow-v010.md
  role: normative
- path: docs/shared-qualification-state-v011.md
  role: normative
- path: docs/result-storage-layout-v009.md
  role: normative
- path: docs/legacy-experiment-retirement-v010.md
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

Accepted v010/C001 worktree-independent shared qualification state authority with combined impact review: preserve every existing registry and checkpoint byte-for-byte; expose the split same-family open-plan conflict; keep completed studies terminal; keep v009/S002 cancelled pending separately approved cross-chain closure; close-invalidated v008/S003 only after successor authority and separate approval; keep v009/S003 paused and restart-on-v011 if no v010 successor study exists before activation. Preserve the v010 fixed-calendar retrospective, non-promotional outcome, policy, release-safety, explicit activation, plan-abandonment, and terminal legacy-archive boundaries.

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

| ID | Title | Status | Outcome | Path |
| --- | --- | --- | --- | --- |
| `S001` | FXI No-ClosePos Cooldown-7 ATR-Floor Dependency-Corrected Fixed-Calendar Retrospective Study | `cancelled` | `-` | [fxi-no-closepos-cooldown-7-atr-floor-dependency-corrected-fixed-calendar-retrospective--s001](work/studies/fxi-no-closepos-cooldown-7-atr-floor-dependency-corrected-fixed-calendar-retrospective--s001/) |
| `S002` | FXI No-ClosePos Cooldown-7 ATR-Floor v011-Bound Evaluation Reexecution Fixed-Calendar Retrospective Study | `paused` | `-` | [fxi-no-closepos-cooldown-7-atr-floor-v011-bound-evaluation-reexecution-fixed-calendar-retrospective--s002](work/studies/fxi-no-closepos-cooldown-7-atr-floor-v011-bound-evaluation-reexecution-fixed-calendar-retrospective--s002/) |

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
