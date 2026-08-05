# Snapshot both market data and research definitions

Every persisted research result references both a research data snapshot and a research definition snapshot. The definition snapshot content-addresses outcome-relevant source content, resolved configuration, runtime and dependency versions, and Git context, including relevant uncommitted content; exported snapshot bundles contain both forms of evidence. This permits exact identification and later reconstruction of research performed from a dirty worktree without requiring a commit for every experimental run.
