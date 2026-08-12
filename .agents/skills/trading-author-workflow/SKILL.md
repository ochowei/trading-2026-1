---
name: trading-author-workflow
description: Create, review, import, evolve, and prepare approved releases for versioned repository research workflows under `workflows/`. Use when turning a repository Markdown or pasted text document into a workflow, guiding workflow design one decision at a time, reviewing authoring gaps, modifying an active workflow through change records, or preparing a workflow release. Do not use to execute studies or draw study conclusions.
---

# Author Trading Workflows

Read `CLAUDE.md` completely before starting. Read
[`references/workflow-authoring-contract.md`](references/workflow-authoring-contract.md) completely
before analyzing or changing a workflow.

## Choose the mode

- Use **review** when the user asks to inspect, assess gaps, or avoid writes. Remain read-only.
- Use **document-led creation** when the user supplies repository Markdown, plain text, or pasted
  text for a new workflow family.
- Use **guided creation** when the user wants to design a workflow through conversation.
- Use **evolution** when the requested slug already exists or the user asks to change an active
  workflow.
- Use **release preparation** only when the user explicitly asks to release an approved draft.

Do not trigger this skill merely because the user wants to execute an existing research workflow.

## Discover before asking

Read `workflows/README.md`, the supplied source, and the exact active workflow when one exists.
Search the repository for relevant code, shared documents, ADRs, references, and inbound links.
Resolve discoverable facts yourself. Classify extracted material as `explicit`, `repository-fact`,
`proposed`, `missing`, or `conflict`; never silently promote `proposed` material into a decision.

Apply this precedence when sources conflict:

1. Repository guardrails and safety rules.
2. The released active workflow for current behavior.
3. User-confirmed decisions as proposed changes.
4. Input documents.
5. Agent recommendations.

## Guide one decision at a time

Ask only unresolved decisions, in dependency order, one question per turn. Include the recommended
answer and its main tradeoff. Skip facts and decisions already explicit in the source. Allow the
user to accept recommendations in bulk only for low-risk details; confirm deletion, release,
authority, and research-validity decisions individually.

Remain read-only until the user confirms shared understanding. Before writing, show the resolved
decision summary, proposed paths, and expected changes.

## Create or import a workflow

1. Confirm an immutable lowercase kebab-case slug and proposed `workflows/<slug>--v001/` path.
2. Check for similar or colliding workflow families. If the slug exists, switch to evolution.
3. Map the source and confirmed decisions into every required `WORKFLOW.md` contract section.
4. Copy `assets/workflow-version/` into the confirmed path and replace every `REPLACE_ME` token.
5. Register the version as `draft` in `workflows/README.md` frontmatter.
6. Run `uv run trading workflow sync` and `uv run trading workflow validate --all`.
7. Keep the source by default. Offer `keep`, `move`, `replace-with-pointer`, or `remove` only after
   the draft validates. Before removal, show the exact path and Git status, warn when an untracked
   source is unrecoverable, and obtain explicit confirmation. Do not use globs.

Never claim an imported workflow was historically active. Initial `v001` starts as a draft and is
released only with current-time approval evidence.

## Evolve an active workflow

Never edit a released `WORKFLOW.md`, including editorial fixes. Record harmless corrections as
README errata and fold them into a later version; use an expedited change when wording can alter
interpretation.

1. Resolve the unique active version from the root registry.
2. Allocate the next unused local `Cxxx` without reusing committed or referenced IDs.
3. Copy `assets/change/` under `<active>/work/changes/<change-slug>--cNNN/` and replace every
   `REPLACE_ME` token.
4. Complete proposal and impact analysis before proposing the change. Complete validation and the
   decision rationale before a human-approved decision transition.
5. Use `uv run trading workflow change transition ...`; never set `released` directly.
6. After one or more changes are accepted, create or update the single next-version draft. Every
   substantive `v002+` rule must trace to an accepted source change.
7. Keep the new version complete and self-contained. Do not implement inherited variants.
8. Run sync and validation after every mutation.

Treat study numbering as local to each exact workflow version. In change impact analysis and
handoff language, refer to “the next CLI-allocated study under vNNN” instead of carrying an `Sxxx`
from the source version or incrementing a family-wide sequence. A replacement version with no
studies starts at `S001`; cross-version continuity is represented only by the exact `revisits` path.

When a similar workflow must remain active in parallel, create a distinct workflow family only
after explicit confirmation. Record the exact `derived_from` workflow version; do not inherit its
rules implicitly.

## Prepare a release

Require explicit human approval and a supplied stable human identifier. Confirm source changes,
combined impact analysis, normative dependencies, and the complete contract. Then run:

```bash
uv run trading workflow release <version-path> --approved-by <human-id>
uv run trading workflow validate --all
```

The command prepares `RELEASE.json` and the intended registry transition. The release becomes
effective only after that commit reaches the canonical branch. Do not infer permission to commit,
push, open a PR, or merge.

## Respect scope

Read studies only to assess version impact. Do not create, preregister, execute, migrate, complete,
or reinterpret studies with this skill. Do not place code, tests, formal results, credentials,
broker exports, private ledger data, or personal trading records under `workflows/`; link exact
immutable evidence identities from their authoritative locations.

Route study creation, preregistration, execution, evidence capture, pause, recovery, and
cancellation to `trading-operate-workflow`. Route independent evidence judgment and terminal study
outcomes to `trading-evaluate-study`.

## Finish

Report the selected mode, files changed, validation results, source disposition, remaining open
decisions, and whether the result is merely a draft, a prepared release, or effective on the
canonical branch.
