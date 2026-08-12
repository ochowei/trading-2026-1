# Firstrade Manual Trading Policy

This policy produces manual proposals only. It does not connect to a broker or authorize automatic
orders. Supported proposal order types are MARKET, LIMIT, and STOP; every proposal has an explicit
duration and immutable identity.

Actual positions come only from confirmed fills in the verified manual execution ledger. A new BUY
requires current successful broker-export reconciliation and the independent workflow, lifecycle,
data, allocation, and drift guards. Missing or stale reconciliation fails closed. Existing verified
positions retain their SELL-management path even while new entries are blocked.

The policy does not define simulated fill prices, research qualification, or sleeve allocation.
