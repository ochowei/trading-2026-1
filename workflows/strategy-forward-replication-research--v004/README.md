---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v004
definition: WORKFLOW.md
supersedes: v003
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v003/work/changes/explicit-unavailable-auxiliary-decisions--c001
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

本版完整保留 v003 的 stages、gates、authority、observation provenance、evidence boundaries 與
legacy protections，並實作 accepted change `strategy-forward-replication-research@v003/C001`。
它採用 `us-equity-market@v002`，允許研究在 outcome 前預註冊 explicit unavailable auxiliary
decisions；maximum lag 仍不可放寬，超齡 decision 必須保留 audit evidence 並禁止 signal。

## Errata

None.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

| ID | Title | Status | Outcome | Path |
| --- | --- | --- | --- | --- |
| `S003` | FXI ATR-Divergence Mean-Reversion Forward Replication | `completed` | `fail` | [fxi-atr-divergence-mean-reversion-forward-replication--s003](work/studies/fxi-atr-divergence-mean-reversion-forward-replication--s003/) |
| `S002` | XLF Close-Armed Profit-Protection Pullback Research | `completed` | `fail` | [xlf-close-armed-profit-protection-pullback--s002](work/studies/xlf-close-armed-profit-protection-pullback--s002/) |
| `S001` | XLF Gap-Safe Rate-Volatility-Conditioned Pullback Research | `completed` | `fail` | [xlf-rate-volatility-conditioned-pullback-gap-safe--s001](work/studies/xlf-rate-volatility-conditioned-pullback-gap-safe--s001/) |

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
