# Use confirmed manual executions as the position authority

Followup strategies produce proposed orders, while actual positions and their stop, target, and expiry instructions are derived only from confirmed fills recorded in a local manual execution ledger. Backtests and unconfirmed proposals never create actual positions, and discrepancies between expected and recorded execution are surfaced for reconciliation rather than silently corrected. This keeps manual Firstrade operation authoritative without introducing broker API integration in the first version.
