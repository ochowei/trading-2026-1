---
policy: us-equity-market
title: US Equity Daily-Bar Market
version: v001
definition: POLICY.md
config: policy.yaml
supersedes: null
implementation:
- src/trading/market_data/calendar.py
- src/trading/market_data/models.py
conformance:
- tests/policies/test_us_equity_market_v001.py
---
# US Equity Daily-Bar Market v001

Draft policy defining the repository's supported adjusted daily-bar market boundary.
