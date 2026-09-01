# Shared Qualification State Authority

## Problem

The qualification registry currently defaults to `state/qualification-registry.json`, so each Git
worktree can silently create a different private append-only hash chain under the same frozen
repository-relative identity. Repository evidence now demonstrates that this happened: one chain
contains the paused v008/S003 plan while another contains the cancelled v009/S002 plan for the same
`fxi-no-closepos-atr-floor-mean-reversion` family. Each chain is internally valid, but neither can
project the other chain's open plan. The family-wide single-open-plan guard therefore depends on
which worktree runs the command.

Selecting one chain as canonical, concatenating JSON events, rewriting event hashes, or copying one
file over another would discard or falsify append-only authority. Leaving the current default in
place would allow the same split to recur for future studies.

## Proposed change

Create a replacement workflow contract and implementation for worktree-independent qualification
state authority:

1. Resolve the default private qualification state from the repository's Git common directory,
   keyed by a stable repository identity, so every worktree uses the same lock, active chain, head
   checkpoint, transaction journal, and study-registration lock.
2. Preserve `state/qualification-registry.json` as the frozen repository-relative logical identity
   used by studies and evidence. Store operational absolute paths separately and never treat a path
   suffix or worktree location as authority.
3. Add a guarded one-time migration that accepts an explicit complete inventory of legacy registry
   and matching head-checkpoint pairs. It verifies every source chain, copies each source byte-for-
   byte into an immutable content-addressed shard, records source path, digest, event count, head
   hash, and migration approval, then publishes one shared authority catalog atomically.
4. Project family-wide open-plan state across every registered shard and the active shared chain.
   A plan is open until a canonical screen or an authorized terminal administration event binds
   that exact plan event, source-shard digest, study identity, and prior head. Missing shards,
   duplicate identities, conflicting terminal events, unregistered local registries, catalog drift,
   or incomplete migration inventory fail closed.
5. Add an append-only, human-approved administrative closure for a plan whose owning study is
   terminal `cancelled` or is a superseded-version paused study with an accepted
   `close-invalidated` impact decision. This event closes only the single-open-plan lock; it does not
   create an outcome, screen, Shadow, activation, broker, order, or live authority.
6. Keep explicit `--path` as a diagnostic and migration-source seam. Normal mutating operations
   must use the verified shared authority unless the frozen operation is an idempotent recovery of
   an already-bound legacy transaction.
7. Publish tracked content-addressed qualification evidence that contains the authority catalog,
   every referenced immutable shard, the active chain, and all matching checkpoints required for
   provider-free replay. Fresh-clone review must not require private runtime state.

## Existing state migration

The first migration inventory must include, without rewriting either source:

- the existing main-checkout chain containing the legacy retrospective plan and the paused
  v008/S003 plan; and
- the existing v009 research chain containing the cancelled v009/S002 plan.

The migration must surface both open plans for
`fxi-no-closepos-atr-floor-mean-reversion`. It must not infer a winner from recency, workflow
version, branch, commit, or filesystem location.

## Public operations

The implementation should provide guarded read-only preview and approved apply operations for the
complete migration inventory, plus shared-state status and verification. Request objects may name
source registry/checkpoint pairs and a destination repository identity, but may not supply event
hashes, derived family state, migration time, or terminal study facts.

The existing v010 `qualification plan abandon` operation remains valid only for a registry in which
the exact plan event is directly present. The successor capability must resolve imported source
plans through their immutable shard identity and apply the new cross-chain terminal administration
rules.

## Non-goals

- Do not rewrite v008, v009, or v010 workflow or study bytes.
- Do not merge event arrays or recompute historical event hashes.
- Do not complete, resume, cancel, review, or reinterpret a study during migration.
- Do not create a Historical Screen, research outcome, promotion, broker, order, position, or live
  authority.
- Do not move trial-registry authority or private broker/manual-ledger data into this store.

## Required validation

Validation must cover shared resolution from multiple worktrees, cross-worktree locking, exact
source/checkpoint verification, immutable shard publication, duplicate and incomplete inventories,
catalog corruption, global single-open-plan projection, cross-chain terminal binding, approved
`close-invalidated` evidence, idempotent retry, crash recovery, evidence snapshot replay, and
continued rejection of caller-selected identities or authority.
