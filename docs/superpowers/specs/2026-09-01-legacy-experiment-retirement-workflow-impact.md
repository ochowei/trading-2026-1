# Legacy Experiment Retirement Workflow Contract Alignment Impact

## Rules, dependencies, and artifacts affected

This change affects the successor workflow's canonical legacy-result namespace, bounded historical
path resolution, normative dependency selection, evidence replay description, and prohibited-use
rules for archived legacy results. It therefore requires a separate accepted change under active
v009 and inclusion in the complete v010 replacement contract.

The v010 metadata must continue to pin `docs/result-storage-layout-v009.md` for the historical v009
categorized-layout rules and additionally pin `docs/legacy-experiment-retirement-v010.md` as a
normative dependency. The v010 contract must state that the latter supersedes the former only for
legacy-result retirement, canonical legacy storage, and the maximum two-hop compatibility
resolution. It must replace the stale single-hop and `results/experiment-results/` statements with
the repository's schema-2, digest-identical retirement boundary.

The implementation and retained evidence already live in their authoritative repository locations:
`src/trading/research_data/paths.py`, `results/registries/path-migrations.json`, `legacy/results/`,
repository architecture and result/archive documentation, and their focused tests. This change
does not move those files, rerun a migration, rewrite frozen artifacts, or introduce a new storage
location.

## Existing studies and qualification plans

- v009 S001 remains immutable `completed/fail`.
- v009 S002 remains terminal `cancelled`; its exact qualification plan remains open, unscreened,
  and unabandoned. This change does not invoke or authorize plan abandonment.
- v009 S003 remains `paused`. Its version-boundary decision remains `restart-on-v010`; it must not
  continue on v009, move to v010, or be rewritten. Any successor effort requires the next
  CLI-allocated v010 study, an exact `revisits` link, and truthful `known-contaminated` disclosure.
- Frozen result paths in existing studies remain unchanged. The bounded two-hop resolver exists to
  preserve their byte-identical replay after retirement.

All active-version studies are already in release-safe lifecycle states: `completed`, `cancelled`,
or `paused`. The paused-study impact decision is explicit here and in accepted v009/C001. No
release-safety assessment is required unless those facts change or a later review finds missing or
conflicting impact evidence.

## Combined impact with accepted v009/C001

The v010 replacement will aggregate two independent changes:

1. accepted C001 adds capability-gated append-only qualification-plan abandonment; and
2. this change aligns legacy-result retirement, archive authority, and two-hop compatibility.

Neither change grants the other's authority. Change acceptance, v010 evolution, release
preparation, Workflow Release Activation, S002 plan abandonment, successor-study creation, and all
study stage approvals remain separate. The combined v010 contract must preserve its fixed-calendar
retrospective scope, non-promotional outcomes, exact policy pins, release-safety capability, and
explicit activation boundary.

## Authority and safety boundaries

The legacy archive is read-only and non-authoritative for new research. It cannot supply result
validity, observations, ranking, qualification evidence, terminal evidence, Shadow registration,
followup new-entry eligibility, or live authority. Compatibility reads and already-owned-position
exit handling remain fail closed and do not permit broker access or new orders.

This change does not alter policy selections, fixed calendars, stages, gates, outcomes, study
lifecycle, qualification lifecycle, private registries, broker state, positions, or orders. It
does not release or activate v010 and does not mark any change `released`.

## Validation plan

Before acceptance, verify:

- proposal and impact completeness and exact v009 ownership;
- schema-2 migration replay, two-hop maximum, same-digest enforcement, cycle/length/drift failure,
  terminal archive existence, and absence of `results/experiment-results/`;
- legacy CLI and result writers remain fail closed while diagnostics remain read-only;
- workflow authoring, source-change, dependency, release, activation, and control-state tests;
- Ruff and format checks;
- non-slow regression;
- workflow and policy validation, path ownership, legacy inventory, and `git diff --check`;
- v009 remains N05, v010 remains N02, C001 remains accepted, this change remains proposed, and no
  study, qualification registry, release, activation, broker, order, or position state changes.
