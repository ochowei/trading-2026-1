---
policy: canonical-execution
title: Canonical Daily-Bar Execution
version: v001
definition: POLICY.md
config: policy.yaml
supersedes: null
implementation:
- src/trading/core/execution_backtester.py
- src/trading/core/sleeve_engine.py
conformance:
- tests/policies/test_canonical_execution_v001.py
---
# Canonical Daily-Bar Execution v001

Draft policy for daily-bar fill behavior and canonical base/stress cost scenarios.
