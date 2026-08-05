# Publish latest results only from valid online runs

`latest.json` advances only after a complete, successful online research run using fresh data and the current research definition. Offline results remain in history, while ephemeral, failed, and partially failed runs do not publish; a previously published latest result remains visible but becomes explicitly data-stale or definition-stale when its validity conditions no longer hold. This preserves backward-compatible result paths without allowing the last attempted execution to masquerade as the current decision-grade result.
