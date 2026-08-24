# Prepare a Workflow Release

Release preparation requires explicit current human approval and a stable human identifier.
Confirm:

- the complete self-contained contract;
- accepted source changes and combined impact;
- the exact active version being replaced, if any;
- safe unfinished-study state from `impact.md`;
- exact released market, broker, execution, and portfolio policy pins;
- normative dependencies and pinned reference companions; and
- absence of unresolved or omitted accepted changes.

Then run:

```bash
uv run trading workflow release <version-path> --approved-by <human-id>
uv run trading workflow validate --all
```

The guarded command generates immutable schema-1 `RELEASE.json` with workflow/version identity,
current-time approval/preparation evidence, human approver, exact `WORKFLOW.md` digest,
`supersedes`, `derived_from`, source changes, dependency digests, and policy release pins. It also
prepares the intended registry transition. Never backdate or hand-author release evidence, set a
change to `released` directly, or rewrite an existing release digest.

A prepared branch release is not effective authority. It becomes effective only when its commit
reaches the canonical branch. Do not infer permission to commit, push, open a PR, merge, execute a
study, promote a strategy, access a broker, or place orders.
