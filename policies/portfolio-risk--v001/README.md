---
policy: portfolio-risk
title: Isolated Sleeve Portfolio Risk
version: v001
definition: POLICY.md
config: policy.yaml
supersedes: null
implementation:
- src/trading/core/sleeve_engine.py
- src/trading/core/manual_ledger.py
- src/trading/core/followup_cutover.py
conformance:
- tests/policies/test_portfolio_risk_v001.py
---
# Isolated Sleeve Portfolio Risk v001

Draft policy for isolated capital, position count, allocation epochs, and fail-closed entries.
