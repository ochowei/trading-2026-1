# Refresh stale results only in explicit evaluation workflows

An explicit asset-evaluation workflow refreshes every stale candidate before producing a complete ranking, while comparison, freshness reporting, and documentation synchronization do not silently rerun experiments. Read-only commands label stale results, documentation synchronization fails closed, and any failed candidate prevents an evaluation from presenting an incomplete set as a complete ranking. This aligns network access and result mutation with the user's command intent.
