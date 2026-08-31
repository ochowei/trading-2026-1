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

Run `uv run trading workflow version state <version-path> --json` before requesting release
approval. Ordinary release preparation starts from exact state `N02`. If predecessor study safety
or paused-study impact evidence is incomplete, stop and route to the release-safety assessment
mode in `safety.md`; do not treat the failed release attempt as authority to create safety evidence.

Then run:

```bash
uv run trading workflow release <version-path> --approved-by <human-id>
uv run trading workflow validate --all
```

The guarded release command generates immutable schema-1 `RELEASE.json` with workflow/version identity,
current-time approval/preparation evidence, human approver, exact `WORKFLOW.md` digest,
`supersedes`, `derived_from`, source changes, dependency digests, and policy release pins. For a
family at or beyond `activation_required_from`, it transitions `draft -> prepared` only. Never
backdate or hand-author release evidence, set a change to `released` directly, or rewrite an
existing release digest.

After a separate current human approval, run:

```bash
uv run trading workflow activate <version-path> --approved-by <human-id>
uv run trading workflow validate --all
```

Activation creates immutable schema-1 `ACTIVATION.json`, binds the exact `RELEASE.json` SHA-256,
transitions `prepared -> active`, supersedes the predecessor, and marks included accepted changes
`released`. Never infer activation from canonical branch membership or `RELEASE.json` presence.

The one-time legacy migration seam is
`trading workflow activation attest <active-version-path> --approved-by <human-id>
--required-from <future-version>`. It records current-time basis
`grandfathered-effective-release`; it never backdates history.

Neither preparation nor activation grants permission to commit, push, open a PR, merge, execute a
study, promote a strategy, access a broker, or place orders.
