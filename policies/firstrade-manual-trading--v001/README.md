---
policy: firstrade-manual-trading
title: Firstrade Manual Trading
version: v001
definition: POLICY.md
config: policy.yaml
supersedes: null
implementation:
- src/trading/core/proposals.py
- src/trading/core/broker_reconciliation.py
- src/trading/core/manual_ledger.py
conformance:
- tests/policies/test_firstrade_manual_trading_v001.py
---
# Firstrade Manual Trading v001

Draft policy for the repository's manual Firstrade-facing order and reconciliation boundary.
