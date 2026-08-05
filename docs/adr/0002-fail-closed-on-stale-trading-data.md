# Fail closed on stale trading data

Trading-facing operations do not produce orders or position-management instructions for a ticker when fresh market data cannot be obtained. Research operations also fail by default, but may use stale data through an explicit offline mode that records the actual data cutoff; a backtest may use cached data only when its requested period is fully covered. This chooses visible unavailability over silently presenting stale analysis as current.
