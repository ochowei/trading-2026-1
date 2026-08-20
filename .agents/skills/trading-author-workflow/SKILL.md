---
name: trading-author-workflow
description: Review, create, import, evolve, abandon, retire, and prepare approved releases for versioned repository research workflows under `workflows/`. Use for workflow authoring and version-impact decisions. Do not execute studies or decide study outcomes.
---

# Author Trading Workflows

Read `CLAUDE.md` completely before starting. Always read `references/core.md`, then load only the
mode references selected below. A named mode reference is mandatory for that mode, not optional
background.

## Route by mode

- **Review:** Read `references/core.md`, then read the reference for the object under review:
  `references/create.md` for a source or initial draft, `references/evolve.md` for a change or
  replacement draft, `references/remove.md` for abandon/retire/removal, or
  `references/release.md` for release readiness. Also read `references/impact.md` when an active
  version or unfinished study may be affected. Remain read-only.
- **Document-led or guided creation/import:** Read `references/create.md`.
- **Evolution of an existing family:** Read `references/evolve.md`. Read `references/impact.md`
  because an active version or its studies may be affected.
- **Abandon, retire, or remove:** Read `references/remove.md`; also read
  `references/impact.md` for an active version.
- **Release preparation:** Read `references/release.md` and `references/impact.md`.

Do not load unrelated mode references. Do not trigger this skill merely because the user wants to
execute or evaluate an existing study.

## Discover before asking

Read `workflows/README.md`, the supplied source, and the exact active workflow when one exists.
Search relevant code, shared documents, ADRs, references, and inbound links. Resolve repository
facts yourself and label extracted material as `explicit`, `repository-fact`, `proposed`, `missing`,
or `conflict`; never silently promote proposed material into a decision.

Ask only unresolved decisions, one at a time and in dependency order. Include the recommended
answer and main tradeoff. Low-risk editorial decisions may be confirmed together; deletion,
identity, authority, research-validity, retirement, and release decisions require individual
confirmation.

Remain read-only until the user confirms shared understanding. Before any write, show the resolved
decision summary, exact proposed paths, expected changes, source disposition, and validation plan.

## Respect authority and scope

The Agent may prepare drafts, change records, and an explicitly approved release command, but is
never the human authority. Do not infer permission to commit, push, open a PR, merge, execute a
study, judge evidence, access a broker, or place orders.

Route study creation, preregistration, execution, evidence capture, pause, recovery, and
cancellation to `trading-operate-workflow`. Route independent evidence judgment and terminal study
outcomes to `trading-evaluate-study`.

## Finish

Report the selected mode and references loaded, files changed, validation results, source
disposition, remaining open decisions, and whether the result is a local draft, prepared release,
or effective canonical release.
