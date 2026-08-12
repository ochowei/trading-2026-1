---
schema_version: 1
policies:
  us-equity-market:
    title: US Equity Daily-Bar Market
    versions:
      v001:
        path: us-equity-market--v001
        status: active
        status_changed_at: '2026-08-12T05:36:39.114580Z'
        status_changed_by: ochowei@gmail.com
  firstrade-manual-trading:
    title: Firstrade Manual Trading
    versions:
      v001:
        path: firstrade-manual-trading--v001
        status: active
        status_changed_at: '2026-08-12T05:36:40.510412Z'
        status_changed_by: ochowei@gmail.com
  canonical-execution:
    title: Canonical Daily-Bar Execution
    versions:
      v001:
        path: canonical-execution--v001
        status: active
        status_changed_at: '2026-08-12T05:36:41.895663Z'
        status_changed_by: ochowei@gmail.com
  portfolio-risk:
    title: Isolated Sleeve Portfolio Risk
    versions:
      v001:
        path: portfolio-risk--v001
        status: active
        status_changed_at: '2026-08-12T05:36:43.254813Z'
        status_changed_by: ochowei@gmail.com
---
# Research Policies

This directory is the canonical registry for composable, executable research policies. A released
workflow selects exact released policy versions; it never resolves an implicit latest version.

<!-- GENERATED:POLICY_INDEX_START -->
| Policy | Version | Status | Path |
| --- | --- | --- | --- |
| Canonical Daily-Bar Execution (`canonical-execution`) | `v001` | `active` | [canonical-execution--v001](canonical-execution--v001/) |
| Firstrade Manual Trading (`firstrade-manual-trading`) | `v001` | `active` | [firstrade-manual-trading--v001](firstrade-manual-trading--v001/) |
| Isolated Sleeve Portfolio Risk (`portfolio-risk`) | `v001` | `active` | [portfolio-risk--v001](portfolio-risk--v001/) |
| US Equity Daily-Bar Market (`us-equity-market`) | `v001` | `active` | [us-equity-market--v001](us-equity-market--v001/) |
<!-- GENERATED:POLICY_INDEX_END -->
