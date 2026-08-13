# Validation

## Evidence and challenge method

Before acceptance, review the proposed semantics against contamination, trial-history, and
non-reuse invariants. Challenge at least these cases: known legacy use; missing provenance;
demonstrably clean holdout; a post-result definition change; overlapping Development and
retrospective sessions; attempted retrospective-to-Historical relabeling; and attempted Shadow
registration from retrospective evidence alone.

Before v005 release preparation, tests must prove that:

- absence of clean evidence classifies a period as `provenance-unknown`;
- only `verified-clean` sessions can populate a Historical plan;
- every asset may opt into a retrospective plan without being called clean;
- frozen annual folds, purge, embargo, costs, challenges, complete family trials, and exact
  identities are recomputed rather than caller asserted;
- retrospective pass projects only `retrospectively-supported` and cannot satisfy Historical,
  Shadow, activation, or live-order gates;
- candidate changes after retrospective inspection invalidate continuity and require a new trial
  or study;
- workflow-native research definitions can register and run plan/screen operations without the
  legacy experiment registry;
- old qualification registries and v004 studies remain byte-stable and verifiable.

The v005 draft and implementation now satisfy these challenges. The domain model serializes an
exact `evidence_role`, `EvaluationEvidenceAudit`, and distinct
`RetrospectiveSelectionCheckpoint`; retrospective plans reject incomplete folds, cannot contain a
future-only `ForwardSelectionEpoch`, and project only `retrospectively-supported` or
`retrospective-screen-failed`. Registry and schema validation reject role/disposition drift and
reject Shadow lineage from retrospective evidence. Historical plans with an explicit audit require
`verified-clean` plus complete trial history. Older events omit the additive fields and continue to
round-trip.

Qualification registration and replay now accept workflow-native `family/trial` identities with
an exact released workflow/policy set. Focused tests prove both paths avoid `get_experiment()`, and
retrospective registration fails unless the released workflow contract explicitly contains the
checkpoint. The compatible legacy option remains available without synthesizing workflow-native
provenance.

Run policy validation, workflow sync and full validation, focused qualification/registry/result
tests, workflow-native definition tests, legacy-inventory guards, Ruff lint and format checks, and
`git diff --check`. The replacement `WORKFLOW.md` and every changed normative dependency must be
pinned by the prepared release.

Validation performed on 2026-08-13:

- `trading workflow validate --all`: passed with v004 active and v005 draft;
- `trading policy validate --all`: passed;
- targeted qualification, Shadow, registry, result-schema, workflow-authoring,
  workflow-native-definition, research CLI, and policy suite: 127 passed;
- Ruff check over all `src/`: passed;
- Ruff format check over all 1,813 `src/` files: passed;
- `git diff --check`: passed.

An attempted unbounded full pytest run reached approximately 10% without a failure but was
interrupted because the market-data-heavy suite was progressing too slowly for this authoring
cycle. It is not recorded as passing. The bounded 127-test regression surface covers every changed
module and governance boundary; the full CI suite remains a release/PR check.

To keep active v004 valid, its pinned shared normative documents were not edited. The v005 draft
instead pins new versioned documents:

- `docs/historical-qualification-and-shadow-v005.md` SHA-256
  `c197b7cd784c25c2e6490fd3159c4cfd3a96aadd70d635075a99f5621c814f3a`;
- `docs/result-validity-and-trial-history-v005.md` SHA-256
  `920eb2fca671bb33c072d22bf8d1030aeff11e477ff5d7823e8c998f0f48a99f`.

The v005 `WORKFLOW.md` SHA-256 is
`ddc379ecf890694744d4e322543c6105646ba7e98bc7e91bdad8628ed2d8da82`.

## Interaction with other accepted changes

No other v004 change currently exists. If another change is accepted before release, combined
impact must be reviewed explicitly; this change must not silently absorb unrelated policy, gate,
data, or activation changes.

## Remaining uncertainty

The implementation uses additive fields inside the existing hash-chained plan/screen event schema
and shares deterministic metric computation while separating role, audit, selection-boundary, and
disposition validation. A future incompatible persistence redesign would require another accepted
change; it is not part of C001.

The change cannot establish that any asset or historical period is clean, that any strategy is
profitable, or that S004 passes. Those are study evidence questions. Canonical effectiveness still
requires explicit v005 release approval, prepared release evidence, full CI/PR review, and merge to
the canonical branch.
