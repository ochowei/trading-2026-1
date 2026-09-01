# Validation

## Evidence and challenge method

Read-only repository and runtime inspection established the split-authority defect before this
change was proposed:

- `trading workflow version state workflows/strategy-forward-replication-research--v010 --json`
  reported exact state `N04`, registry status `active`, and no unfinished v010 studies.
- The default `trading qualification status` in the current worktree reported an empty registry,
  proving that the logical default currently resolves per worktree.
- The main-checkout `state/qualification-registry.json` replayed two internally valid
  `historical_plan` events. One is the exact paused v008/S003 plan for
  `fxi-no-closepos-atr-floor-mean-reversion`.
- The v009 research worktree registry replayed one internally valid `historical_plan` event for the
  exact cancelled v009/S002 study and the same experiment family.
- Running the current v010 code with `trading qualification status --path <v009-registry>`
  provider-free verified the second chain and reported plan
  `retrospective-plan-c38e1fbe354068c8a161381583f7538b228ba1a4181ff258bef650b1917111a8`
  as `historical-screen-pending`.
- The existing CLI exposes `--path`, but its default is the relative
  `state/qualification-registry.json`. Structured study compilation requires the operational path
  to resolve from the frozen repository-relative identity, so merely passing a different file does
  not create a shared default or a cross-chain single-open-plan projection.
- `QualificationRegistry` derives its head checkpoint, mutation lock, study-registration lock, and
  transaction journal from the operational registry path. A safe shared design must therefore move
  all coordination paths together; a registry-only symlink or copied JSON file is insufficient.
- Existing qualification evidence snapshots preserve one source chain at a time. They verify bytes
  and checkpoints but do not provide a mutable merge or federation authority.

These observations reject the unsafe alternatives of choosing the newest file, concatenating event
arrays, rewriting hashes, copying one registry over another, or starting a new empty registry.

The implementation validation for the successor must include focused unit and CLI tests for shared
Git-common resolution, complete migration inventory, immutable shard replay, global plan
projection, cross-chain administration, concurrent writers, pending journals, idempotent recovery,
and tracked evidence snapshots. It must also run Ruff, the non-slow regression suite, workflow and
policy validation, path-ownership checks, and a fresh-clone/provider-free replay test.

## Interaction with other accepted changes

Active v010 contains released qualification-plan abandonment and legacy experiment retirement
changes inherited from v009/C001 and v009/C002. This proposal preserves both boundaries. It extends
administrative plan termination only through a successor capability that binds an exact imported
source chain and accepted impact evidence.

There are no other accepted changes under v010 at proposal time. If another change is accepted
before v011 evolution, combined impact review must prove that its registry, evidence, study, or
release behavior is compatible with the shared authority catalog.

## Remaining uncertainty

The replacement design must still freeze the exact repository-identity derivation, shared catalog
schema, immutable shard naming, crash-recovery journal, and cross-chain terminal event schema before
implementation. It must also produce a complete operator-reviewed source inventory; the two known
registries are mandatory inputs but must not be assumed to be the complete machine-wide set without
a fail-closed discovery check.

The proposed `close-invalidated` impact for paused v008/S003 and `restart-on-v011` impact for paused
v009/S003 require an explicit human change decision. Until then, both studies and all existing plan
events remain unchanged, and no new family plan may rely on the proposed behavior.
