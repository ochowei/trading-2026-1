---
policy: us-equity-market
title: US Equity Daily-Bar Market
version: v002
definition: POLICY.md
config: policy.yaml
supersedes: v001
implementation:
- src/trading/market_data/calendar.py
- src/trading/market_data/models.py
- src/trading/market_data/availability.py
- src/trading/market_data/bundle.py
- src/trading/research_data/manifest_codec.py
conformance:
- tests/policies/test_us_equity_market_v002.py
---
# US Equity Daily-Bar Market v002

Draft replacement adding explicit, auditable unavailable-decision handling for sparse auxiliary
series while preserving v001 fail-closed behavior as the default.
