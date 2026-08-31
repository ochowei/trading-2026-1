# Core Workflow Authoring Rules

## Repository precedence

Apply sources in this order:

1. Repository guardrails and safety rules.
2. The released active workflow for current behavior.
3. User-confirmed decisions as proposed changes.
4. Input documents.
5. Agent recommendations.

Stop and report a conflict rather than choosing a weaker rule.

## Identity and layout

A workflow family is one repeatable end-to-end decision process with its own trigger, inputs,
outputs, and terminal states. A phase, asset, experiment, or study is not a workflow family.

Use immutable lowercase ASCII kebab-case family paths:

```text
workflows/<stable-slug>--vNNN/
```

Each family starts at `v001`; `v002` replaces `v001` rather than creating a parallel variant.
Create a distinct family with exact `derived_from` metadata only when both procedures must remain
active. Never inherit rules implicitly or rename an allocated directory.

Use English ASCII for paths, filenames, metadata keys, IDs, and lifecycle values. Traditional
Chinese may be used for explanatory prose. Do not maintain two authoritative translations.

`workflows/README.md` schema-1 frontmatter is the lifecycle authority. Derive the current version
from the unique `active` entry; allow at most one `active` and one candidate in either `draft` or
`prepared` per family. `prepared` means release evidence exists but authority has not switched.
New families declare `activation_required_from: v001`; migrated families declare their confirmed
future boundary. Preserve `superseded`, `retired`, and `abandoned` entries permanently.

## Complete contracts and exact dependencies

Every `WORKFLOW.md` must be independently readable and cover:

1. purpose and decision;
2. scope and non-goals;
3. entry conditions and inputs;
4. roles and authority;
5. stages and transitions;
6. invariants and prohibited behavior;
7. artifacts and evidence;
8. pass, fail, insufficient-evidence, and indeterminate outcomes;
9. pause, recovery, and termination;
10. version-changing behavior; and
11. shared technical documents and implementation links.

Behavioral rules belong in the workflow contract, not only behind links. CLI validation checks
structure and identity; Agent and human review semantic completeness.

Every release selects exact released market, broker, execution, and portfolio policy versions. A
draft may temporarily carry a null policy release digest only while that selected policy is itself
an unreleased draft; release preparation requires the exact released policy identity and digest.
Classify shared documents as `normative` or `reference`. Release preparation pins normative bytes
and any explicitly pinned reference companion; never resolve implicit `latest`.

Keep shared code, tests, technical contracts, formal results, and ADRs in their authoritative
repository locations. Link immutable evidence identities rather than copying content into
`workflows/`. Never store credentials, broker exports, holdings, private ledgers, or raw private
trading data there.

## Validation and authority

Use three layers:

1. CLI validates structure, paths, metadata, lifecycle, indexes, hashes, and exact references.
2. Agent validates semantic fidelity, change coverage, and impact reasoning.
3. Humans approve change decisions, retirement, release preparation, and Workflow Release
   Activation; an independent reviewer confirms study outcomes.

Run after every write:

```bash
uv run trading workflow sync
uv run trading workflow validate --all
```

High-level authoring previews pin the current target digests. If apply reports target drift or an
invalid partial worktree, do not bypass the guard: inspect the repository, regenerate a fresh
preview, and obtain confirmation again when its resolved changes differ. The authoring lock does
not grant authority and does not coordinate study or qualification operations.

CI must fail closed on validation issues. Release preparation does not authorize activation,
commit, push, merge, study execution, promotion, or trading.
