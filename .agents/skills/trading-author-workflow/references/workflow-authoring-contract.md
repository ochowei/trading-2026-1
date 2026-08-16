# Workflow Authoring Contract

## Contents

- [Ownership and identity](#ownership-and-identity)
- [Repository layout](#repository-layout)
- [Root registry](#root-registry)
- [Version metadata](#version-metadata)
- [Workflow contract](#workflow-contract)
- [Version lifecycle](#version-lifecycle)
- [Change records](#change-records)
- [Study operation and version impact](#study-operation-and-version-impact)
- [Release evidence](#release-evidence)
- [Dependencies and shared artifacts](#dependencies-and-shared-artifacts)
- [Source import](#source-import)
- [Validation and authority](#validation-and-authority)

## Ownership and identity

A workflow family is one repeatable, end-to-end decision process with its own trigger, inputs,
outputs, and terminal states. A technical phase, asset, experiment, or individual study is not a
workflow family.

Treat the workflow directory as a long-lived knowledge and governance hub. Keep shared code,
tests, formal results, common technical contracts, and ADRs in their authoritative repository
locations; link them precisely instead of copying them.

Use the stable semantic slug as family identity and a local version suffix as replacement lineage:

```text
workflows/<stable-slug>--vNNN/
```

- Use lowercase ASCII kebab-case slugs.
- Start each family at `v001`; different families may each have `v001`.
- Interpret `v002` as replacing `v001`, never as a parallel variant.
- Never reuse a committed or referenced version number, including abandoned drafts.
- Create a distinct family with exact `derived_from` metadata when similar processes must coexist.
- Treat complete directory names as immutable after creation.

## Repository layout

```text
workflows/
├── README.md
└── <slug>--vNNN/
    ├── README.md
    ├── WORKFLOW.md
    ├── RELEASE.json              # generated only for released versions
    └── work/
        ├── studies/
        │   └── <study-slug>--sNNN/
        │       ├── README.md
        │       ├── HYPOTHESIS.md
        │       ├── PLAN.md
        │       ├── EVIDENCE.md
        │       ├── CONCLUSION.md
        │       ├── PREREGISTRATION.json # generated after human approval
        │       └── COMPLETION.json      # generated only at completion
        └── changes/
            └── <change-slug>--cNNN/
                ├── README.md
                ├── PROPOSAL.md
                ├── IMPACT.md
                ├── VALIDATION.md
                └── DECISION.md
```

Do not create empty placeholder directories merely for Git. Create `work/changes/` on the first
change and leave study creation to `trading-operate-workflow`.

Use English ASCII for paths, filenames, metadata keys, IDs, and state values. Use Traditional
Chinese for explanatory prose when appropriate. Do not maintain two authoritative translations.

## Root registry

`workflows/README.md` is the only authority for version lifecycle state. Store a complete version
registry in YAML frontmatter and generate the human-readable table from it:

```yaml
---
schema_version: 1
workflows:
  example-workflow:
    title: 範例流程
    versions:
      v001:
        path: example-workflow--v001
        status: superseded
        status_changed_at: "2026-08-11T00:00:00.000000Z"
        status_changed_by: reviewer-id
      v002:
        path: example-workflow--v002
        status: active
        status_changed_at: "2026-08-12T00:00:00.000000Z"
        status_changed_by: reviewer-id
---
```

Derive the current version from the unique `active` entry; do not store a second `current` field.
Allow at most one `active` and one `draft` per family. Preserve `superseded`, `retired`, and
`abandoned` entries permanently.

## Version metadata

Put immutable identity and authoring inputs in the version README frontmatter:

```yaml
---
workflow: example-workflow
title: 範例流程
version: v002
definition: WORKFLOW.md
supersedes: v001
derived_from: null
source_changes:
  - workflows/example-workflow--v001/work/changes/example-change--c001
policies:
  - family: us-equity-market
    version: v001
    path: policies/us-equity-market--v001
    release_digest: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
dependencies:
  - path: docs/example-contract.md
    role: normative
  - path: docs/example-background.md
    role: reference
---
```

For a new family, set `supersedes: null` and `source_changes: []`. For a derived family, set
`derived_from` to exactly `workflow`, `version`, and repository-relative `path`. This records
lineage only and never causes inheritance.

Every `v002+` substantive rule must trace to one or more accepted source changes. A release may
aggregate multiple accepted changes, but must assess their combined effects.

Every new workflow release must select exact released policy versions. Draft metadata may use a
null `release_digest` while its policy dependencies remain drafts, but release preparation requires
the exact SHA-256 of each selected policy's `RELEASE.json`. Never resolve an implicit active/latest
policy, duplicate one family, or select a retired/unreleased policy.

## Workflow contract

Keep `WORKFLOW.md` complete and independently readable. Include these sections even when brief:

1. Purpose and decision answered.
2. Scope and non-goals.
3. Entry conditions and required inputs.
4. Roles, authority, and responsibility.
5. Stages and state transitions.
6. Invariants and prohibited behavior.
7. Required artifacts and evidence per stage.
8. Pass, fail, insufficient-evidence, and indeterminate outcomes.
9. Pause, recovery, and termination behavior.
10. Changes that require a new workflow version.
11. Shared technical documents and implementation links.

Keep behavioral rules in the contract rather than hiding them behind links. Narrative section
headings may be translated; the semantic coverage is mandatory and is reviewed by the Agent and
human, not guessed by the structural CLI.

## Version lifecycle

Use these one-way states:

```text
draft -> active -> superseded
                -> retired
draft -> abandoned
```

- Edit a draft until its approved scope is complete.
- Make an initial `v001` from confirmed authoring decisions without source changes.
- For `v002+`, allow only rules traceable to accepted changes.
- Never edit a released `WORKFLOW.md`, including editorial corrections.
- Record harmless corrections as README errata and include them in a later version.
- Use an expedited change and new version when wording can alter interpretation.
- Never recycle abandoned version numbers.
- Prepare releases on a branch; they become effective only when merged to the canonical branch.

Use `workflow version transition` only for `draft -> abandoned` and `active -> retired`. Let
`workflow release` create `active` and `superseded` transitions.

## Change records

Scope change IDs to the source version. Use a stable semantic suffix path:

```text
<change-slug>--cNNN/
```

The full identity is `<workflow>@<source-version>/Cxxx`. Start at `C001` within each version and
never reuse committed or referenced IDs.

Store this minimum README metadata:

```yaml
---
id: C001
title: Example change
workflow: example-workflow
source_version: v001
status: draft
created_at: "2026-08-11"
status_changed_at: null
decided_at: null
decided_by: null
released_in: null
---
```

Use the lifecycle:

```text
draft -> proposed -> accepted -> released
                  -> rejected
                  -> deferred -> proposed
draft/proposed/deferred -> withdrawn
```

- Complete `PROPOSAL.md` and `IMPACT.md` before `proposed`.
- Complete `VALIDATION.md` and `DECISION.md` before `accepted`, `rejected`, or `deferred`.
- Require explicit human identity for decisions.
- Distinguish `rejected` (evaluated and declined), `deferred` (awaiting evidence), and `withdrawn`
  (stopped before decision).
- Let only workflow release set `released` and `released_in`.
- Keep source changes under the version they modify. The replacement version links back; do not
  copy the records.

## Study operation and version impact

A workflow is a versioned procedure definition. A study is one execution instance pinned to one
released workflow version. Use `trading-operate-workflow` for execution and
`trading-evaluate-study` for independent judgment; workflow authoring must not perform either role.

Scope study IDs to the pinned workflow version. Let the CLI allocate the next never-reused local
`Sxxx` and use:

```text
<study-slug>--sNNN/
```

Store this minimum README metadata:

```yaml
---
id: S001
title: Example study
workflow: example-workflow
workflow_version: v001
status: draft
outcome: null
created_at: "2026-08-11T00:00:00.000000Z"
created_by: researcher-id
status_changed_at: null
status_changed_by: null
status_reason: null
preregistered_at: null
preregistered_by: null
completed_at: null
reviewed_by: null
revisits: null
---
```

Use this lifecycle:

```text
draft -> preregistered -> running -> awaiting-review -> completed
                           |  ^             |
                           v  |             └-> running
                         paused

draft/preregistered/running/paused -> cancelled
```

- Create and preregister new studies only under the active workflow version.
- Require complete `HYPOTHESIS.md` and `PLAN.md` plus explicit human approval before
  preregistration.
- Generate `PREREGISTRATION.json` at the current time. Pin the workflow, hypothesis, and plan
  SHA-256 values; never accept a backdated timestamp.
- Never change hypothesis or plan after preregistration. Cancel and create a new study with an
  exact `revisits` path when the research design changes.
- Let the operator follow the frozen workflow and record exact immutable evidence identities. The
  operator may not choose or write an outcome.
- Require complete evidence before `awaiting-review`. Only an independent evaluation may write
  `CONCLUSION.md` and move the study to `completed`.
- Use only `pass`, `fail`, `insufficient-evidence`, or `indeterminate` as terminal outcomes.
- Generate `COMPLETION.json` at completion, pinning preregistration, evidence, conclusion, outcome,
  time, and reviewer identity. Never edit completed artifacts.
- Require reasons for pause and cancellation. Treat `completed` and `cancelled` as terminal.
- Permit a reviewer to return `awaiting-review -> running` only with a reason and without changing
  the frozen design.

Use guarded CLI transitions instead of editing lifecycle metadata directly:

```bash
uv run trading workflow study init <active-version-path> \
  --slug <study-slug> --title <title> --created-by <identity>
uv run trading workflow study preregister <study-path> --approved-by <human-id>
uv run trading workflow study transition <study-path> --to running --by <identity>
uv run trading workflow study transition <study-path> --to awaiting-review --by <identity>
uv run trading workflow study complete <study-path> --outcome <outcome> \
  --reviewed-by <identity>
```

When a released capability requires route-scoped qualification, initialization must include the
exact `--route`, first Development must include its separate `--approved-by`, and candidate freeze
must use the add-only current-time writer rather than a hand-authored artifact:

```bash
uv run trading workflow study freeze-candidate <study-path> \
  --selection <development-selection.json> --approved-by <human-id>
```

The selection input may contain only the outcome-derived selected candidate, distinct baseline,
and ordered complete family. Approval time, scope, exact study digests, and trial budget belong to
the guarded writer. Exact-study qualification plans must persist repository-relative registry
identities separately from operational absolute paths so tracked fresh-clone replay never depends
on path-suffix matching.

When a new version replaces or retires an active version, first move every unfinished study to a
safe state. The CLI permits the version boundary only when each study is `paused`, `completed`, or
`cancelled`. The change impact must assign every paused old study one explicit disposition:

- `continue-on-vNNN`
- `restart-on-vNNN`
- `close-invalidated`

Never move or overwrite an old study. Create a new local study ID under the replacement version
and record an exact `revisits` path when research restarts or continues there.

## Release evidence

`workflow release` generates immutable `RELEASE.json` containing:

- schema version, workflow slug, and version;
- current-time `approved_at` and `prepared_at` without a backdating option;
- explicit human `approved_by`;
- exact `WORKFLOW.md` SHA-256;
- `supersedes`, `derived_from`, and source changes;
- dependencies, including SHA-256 for normative dependencies.
- exact policy family, version, path, and policy-release digest pins.

Do not write `released_at` before merge. Treat the canonical-branch merge as the effective release
boundary. Never rewrite an old release digest.

## Dependencies and shared artifacts

Classify every shared link:

- `normative`: required for correct workflow execution. Pin its exact SHA-256 at release. A change
  affecting the active workflow requires a new workflow version.
- `reference`: background or implementation detail. It may point to the current document and does
  not define workflow validity.

A reference companion whose exact released bytes must remain stable uses `pinned: true`. Release
preparation records its SHA-256 and validation rejects later drift, while its `reference` role
continues to mean that `WORKFLOW.md` alone defines behavior.

Use versioned policy pins—not mutable document dependencies—for reusable market, broker,
execution, and portfolio constraints. Different workflows may select different released policy
versions. A policy adoption change requires a new workflow version but never rewrites an old study.

Keep common code, tests, formal results, technical contracts, and ADRs at one authoritative path.
Do not copy them into each workflow version. Formal evidence must use immutable result manifests,
snapshot IDs, complete commit SHAs, and checksums rather than mutable `latest` references alone.

Treat all of `workflows/` as Git-tracked and shareable. Never store credentials, broker exports,
private ledgers, personal holdings, or raw private trading data there.

## Source import

Directly accept repository Markdown/plain text or pasted text. Require other formats to be
extracted before this skill handles them.

Read a source without mutation. Record its path, commit, and checksum when available, then map its
claims to the workflow contract. Ask about only missing, proposed, or conflicting decisions. Keep
the source by default.

After the new draft validates, offer:

- `keep`
- `move`
- `replace-with-pointer`
- `remove`

Before `remove`, display the exact source path and Git status, warn that untracked content cannot
be recovered from Git, and require explicit confirmation. Direct deletion is allowed after that
confirmation; do not create an automatic provenance copy and never use a glob.

## Validation and authority

Use three layers:

1. CLI validates structure, paths, metadata, lifecycle, indexes, hashes, and exact references.
2. Agent validates semantic fidelity, change coverage, and impact reasoning.
3. Human approves preregistration, change decisions, and release authority; an identified,
   independent reviewer confirms study outcomes.

The Agent may prepare and execute an explicitly approved release command, but is never the release
authority. Do not infer permission to commit, push, open a PR, or merge.

Run after every write:

```bash
uv run trading workflow sync
uv run trading workflow validate --all
```

CI must fail closed when validation reports any issue.
