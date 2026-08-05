# Record manual execution as append-only events

The manual execution ledger is an append-only CSV event record, and actual positions, cash, and cost basis are projections rebuilt from its submitted, fill, partial-fill, cancellation, fee, and correction events. Existing events are not edited or deleted; corrections are new events, writes are serialized and atomic, and any generated position file is disposable rather than authoritative. This preserves auditability and deterministic reconciliation while retaining a human-readable local file format.
