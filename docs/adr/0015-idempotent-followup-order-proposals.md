# Make followup order proposals idempotent

Each proposed order has a deterministic proposal ID derived from its strategy sleeve, instrument, signal and trading dates, action, and position identity. Repeated followup runs preserve that identity, confirmed execution events reference it, daily replacement orders receive session-specific identities tied to the same position, and changed terms for an existing proposal are surfaced as conflicts rather than overwritten. This prevents repeated report generation from becoming repeated manual orders.
