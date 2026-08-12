# Isolated Sleeve Portfolio Risk Policy

Each instrument slot receives an isolated strategy sleeve. A sleeve does not borrow from another
sleeve or the unallocated reserve, holds at most one open position, and does not pyramid. Canonical
research uses equal initial sleeves with no within-evaluation rebalancing.

Managed-capital allocation changes only through an explicit allocation epoch. New entries fail
closed when lifecycle, result, data, ledger, broker reconciliation, allocation, or drift evidence is
missing or invalid. Blocking new entries does not abandon management of an existing verified
position.

The policy does not define signals, market-data availability, or fill-price assumptions.
