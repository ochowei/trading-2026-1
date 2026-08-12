# Versioned research policies

`policies/` contains composable market, broker, execution, and portfolio-risk contracts. Each
version binds a human-readable `POLICY.md`, strict `policy.yaml`, implementation paths, and focused
conformance tests. Drafts are editable; released versions and their pinned dependencies are
immutable.

Workflows must select exact released family/version identities. They never inherit the active or
latest policy implicitly. Superseded releases remain resolvable for historical workflows and
studies, while retired releases cannot be selected by a new workflow release.

Use:

```bash
uv run trading policy sync
uv run trading policy validate --all
uv run trading policy release policies/<family>--vNNN --approved-by <human-id>
uv run trading policy version transition policies/<family>--vNNN --to retired \
  --approved-by <human-id>
```

Release preparation requires explicit human authority and becomes effective only when its commit
reaches the canonical branch. Tracked policies must never contain broker exports, credentials,
holdings, private ledgers, or personal trading records.
