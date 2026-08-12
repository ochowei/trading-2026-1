---
workflow: strategy-forward-replication-research
title: 策略前瞻驗證流程
version: v003
definition: WORKFLOW.md
supersedes: v002
derived_from: null
source_changes:
- workflows/strategy-forward-replication-research--v002/work/changes/document-observation-provenance--c001
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

本版完整保留 v002 的研究 stages、gates、authority boundaries、policy pins、legacy
protections 與 completed-study identities，並實作 accepted change
`strategy-forward-replication-research@v002/C001`。該 change 明確定義 workflow-native formal
result 的 `metadata.observation_provenance` wire contract、exact orchestration source capture 與
tracked/local-only storage boundary，使 workflow、implementation、reproducibility 與 result
documentation 保持一致。

## Errata

The S003 cancellation reason used “replacement S004” as shorthand for the fourth XLF research
round. Study IDs are scoped to the exact workflow version; no `S004` was allocated. Any restart
under v004 is its first CLI-allocated study (`S001`) and preserves lineage only through `revisits`.

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

| ID | Title | Status | Outcome | Path |
| --- | --- | --- | --- | --- |
| `S001` | XLF Rate-Volatility-Conditioned Pullback Research | `cancelled` | `-` | [xlf-rate-volatility-conditioned-pullback--s001](work/studies/xlf-rate-volatility-conditioned-pullback--s001/) |
| `S003` | XLF Rate-Volatility-Conditioned Pullback Publication-Lag-Safe Research | `cancelled` | `-` | [xlf-rate-volatility-conditioned-pullback-publication-lag-safe--s003](work/studies/xlf-rate-volatility-conditioned-pullback-publication-lag-safe--s003/) |
| `S002` | XLF Rate-Volatility-Conditioned Pullback Revised Availability Research | `cancelled` | `-` | [xlf-rate-volatility-conditioned-pullback-revised-availability--s002](work/studies/xlf-rate-volatility-conditioned-pullback-revised-availability--s002/) |

### Changes

| ID | Title | Status | Released in | Path |
| --- | --- | --- | --- | --- |
| `C001` | Explicit Unavailable Auxiliary Decisions | `released` | `v004` | [explicit-unavailable-auxiliary-decisions--c001](work/changes/explicit-unavailable-auxiliary-decisions--c001/) |
<!-- GENERATED:WORK_INDEX_END -->
