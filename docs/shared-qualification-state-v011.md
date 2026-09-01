# Shared Qualification State v011

This document defines the worktree-independent private qualification-state authority introduced by
`strategy-forward-replication-research@v011`. It preserves existing registry bytes and study
identities while making family-wide lifecycle checks independent of the caller's Git worktree.

## Logical identity and operational authority

Frozen studies continue to use the repository-relative logical identity
`state/qualification-registry.json`. That string is evidence identity, not an instruction to create
one mutable registry per worktree.

The runtime resolver derives one shared private state root from the repository's verified Git common
directory and a stable repository identity. All worktrees for that repository must resolve the same
authority catalog, active registry chain, head checkpoint, mutation lock, study-registration lock,
and transaction journal. An explicit diagnostic path cannot replace the shared authority for a new
mutation.

Missing Git-common identity, ambiguous repository ownership, a worktree-local default registry, or
different resolved paths for related locks and journals fails closed. The shared store is local-only,
ignored by Git, contains no broker data, and must be backed up separately from tracked evidence.

## Store layout

The shared store contains:

- an immutable content-addressed shard for every imported registry JSON plus its exact head
  checkpoint;
- an append-only authority catalog binding the repository identity, migration generation, shard
  digests, event counts, head hashes, logical source identities, source attestations, and current
  active-chain identity;
- one active append-only registry and matching checkpoint for successor administrative and research
  events;
- shared locks and a recoverable transaction journal covering catalog, shard, active-chain, and
  study-registration publication.

Shard filenames derive only from verified content. Source paths are audit context and never
authority. Imported shards are immutable; all later facts are appended to the active chain and bind
the exact source shard, plan event, study, and prior shared head.

## Guarded migration

Migration is a separately human-approved administration operation. The request supplies a complete
explicit inventory of source registry/checkpoint pairs and stable approver identity. The writer
derives all digests, event counts, head hashes, families, plans, and study bindings.

Before publication it must:

1. hold one repository-wide shared migration lock;
2. reject any source with a mutation lock held, pending transaction journal, missing checkpoint,
   malformed chain, digest mismatch, unsafe path, duplicate bytes under conflicting metadata, or
   event-identity collision;
3. verify every registry through the authoritative reader;
4. discover and report all open plans across the complete inventory;
5. stage byte-identical immutable shards, catalog, active chain, checkpoints, and journal;
6. obtain a commit decision binding the exact source inventory and bytes; and
7. atomically publish or idempotently recover only that exact decision.

The initial migration for this repository must include the known main-checkout chain and the known
v009 research chain. Discovery of any additional unregistered qualification registry blocks apply
until the request and approval cover the complete inventory. Migration never deletes source bytes;
after verified publication they become non-authoritative recovery inputs and must be clearly marked
against future mutation.

The maintained operator interface is:

```text
trading qualification shared-state migration-preview \
  --request <closed-request.json> --workflow <v011-path> --repository-root <repo>

trading qualification shared-state migration-apply \
  --request <same-request.json> --workflow <effective-v011-path> \
  --approved-decision-sha256 <exact-preview-digest> --repository-root <repo>
```

The closed request has schema version 1, the logical registry identity, stable `approved_by`, and
one explicit absolute `registry_path` plus canonical `checkpoint_path` for each source. Preview is
read-only and may run against the structurally valid v011 draft for release readiness. Apply first
requires exact effective capabilities and an approval digest matching the newly recomputed preview;
therefore draft v011 cannot publish state even if implementation code is installed.

## Global lifecycle projection

Readers replay every registered immutable shard and the active chain. Plan identity and family-open
state are global across the catalog. A `historical_plan` is open unless exactly one valid
`historical_screen` or administrative terminal event closes that exact plan.

Duplicate plan IDs, duplicate terminal facts, terminal facts preceding their source plans,
conflicting family or study bindings, an unregistered chain, or an omitted catalog shard fails
closed. Workflow version, branch, commit recency, filesystem location, and source modification time
cannot select a winning chain.

All new plan registration, screen, challenge, replay, terminal review, and study-completion guards
must use the same shared projection and shared locks. A worktree-local `--path` may be read for
diagnosis or named as an approved migration source, but cannot authorize ordinary mutation.

## Cross-chain administrative terminal events

The active chain may append a terminal administration event only when it binds:

- the exact source shard digest, source head hash, plan event hash, plan ID, family, and frozen study
  identity;
- the canonical current study lifecycle identity and exact authorizing active workflow release;
- current UTC, stable human approver, concrete reason, and the shared catalog/active-chain prior
  head; and
- the applicable accepted version-impact evidence and digest.

For a terminal `cancelled` study, the existing qualification-plan-abandonment semantics remain:
the event closes only the administrative family lock and creates no outcome.

For a paused study pinned to a superseded workflow, cross-chain closure additionally requires an
accepted `close-invalidated` impact decision that names the exact study. This event records
`historical_plan_closed_invalidated`; it does not cancel, complete, move, resume, review, or assign an
outcome to the study. A paused study without that evidence remains open.

Screened plans, already terminal plans, completed-study plans, active-version paused plans, legacy
plans without exact study binding, and caller-selected study paths are ineligible. Every terminal
operation is separately approved and idempotent only for identical content.

The terminal interface is `trading qualification shared-state close-plan`. It requires the exact
plan ID, `cancelled` or `close-invalidated` disposition, effective v011 path, accepted change
directory, stable `approved_by`, concrete reason, and repository root. It derives the owning study
from the imported plan; no caller-supplied study path is accepted.

## Evidence and replay

Tracked content-addressed qualification evidence for shared state contains the authority catalog,
all referenced immutable shards and checkpoints, the active chain and checkpoint, and their exact
digests. The evidence resolver replays the same global projection provider-free and verifies the
logical registry identity frozen by the study.

Tracked evidence never exposes credentials, broker exports, holdings, private ledgers, or raw
private trading data. A fresh clone can review terminal facts from tracked evidence without
reconstructing mutable shared state, but cannot perform a new mutation without the private shared
store.

`trading qualification shared-state evidence-snapshot --repository-root <repo>` publishes this
schema-2 bundle under the tracked qualification-evidence directory. Resolution verifies the outer
digest, catalog digest, every registry/checkpoint digest and authoritative registry replay before
projecting global open plans; it does not require Git-common mutable state or a data provider.

## Recovery and authority boundary

Recovery may finish only an existing commit decision with the same inventory, digests, repository
identity, approver, catalog head, and active-chain head. Different source bytes or newly discovered
registries require a new preview and approval. Partial publication, missing shards, catalog drift,
or uncertain lock ownership pauses all qualification mutations.

Shared-state migration, catalog publication, plan closure, workflow release, workflow activation,
study operation, outcome review, and trading authority are separate. None implies another. No
operation defined here creates Historical pass/fail, Shadow, promotion, broker, order, position, or
live authority.
