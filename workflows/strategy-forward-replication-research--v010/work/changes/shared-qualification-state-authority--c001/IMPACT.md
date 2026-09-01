# Shared Qualification State Authority Impact

## Workflow and policy impact

This changes qualification-registry authority, operational path resolution, locking scope,
migration evidence, terminal plan administration, and the family-wide single-open-plan projection.
Those are normative workflow behaviors, so the change requires an accepted record under active
v010 and a complete v011 replacement. Released v010 bytes remain immutable and authoritative until
v011 completes release preparation and explicit Workflow Release Activation.

The selected market, broker, execution, and portfolio policies do not change. The replacement must
retain the fixed-calendar retrospective route, non-promotional outcome boundary, explicit workflow
activation, qualification-plan abandonment, workflow release safety, and legacy archive rules
unless another independently accepted change says otherwise.

## Existing registries and plans

Two internally valid private chains currently share the logical identity
`state/qualification-registry.json`:

- The main-checkout chain contains two open Historical plans, including the paused v008/S003 plan
  for `fxi-no-closepos-atr-floor-mean-reversion`.
- The v009 research chain contains the cancelled v009/S002 plan for the same family and has no
  screen or abandonment event.

The v009/S002 plan was registered without observing the other chain's open family plan. Migration
must preserve this fact as a detected split-authority conflict. It must not retroactively claim that
the single-open-plan gate passed globally.

No existing registry file or head checkpoint may be overwritten, truncated, concatenated, or
selected as the sole historical truth. Source locks and pending transaction journals must be
checked before migration; a source with an unresolved journal or mismatched checkpoint blocks the
operation.

## Existing studies

- Completed v008 and v009 studies remain completed with their bytes and outcomes unchanged.
- Cancelled v009/S002 remains terminal `cancelled`. After shared migration and a separate current
  human approval, its exact open plan may receive the successor's cross-chain administrative
  closure. That closure remains non-outcome evidence.
- Paused v008/S003 remains pinned to v008. Its prior `continue-on-v008` decision is no longer
  executable after v008 became superseded. The proposed replacement impact is
  `close-invalidated`, but it becomes authority only through an accepted change decision and the
  successor's guarded cross-chain closure; authoring this proposal does not change the study or
  plan.
- Paused v009/S003 remains pinned to v009 and must not be moved or resumed. If v011 becomes active
  before a v010 successor study is created, its replacement-version decision becomes
  `restart-on-v011`; any successor is the next CLI-allocated local study with an exact `revisits`
  link and truthful `known-contaminated` disclosure.
- v010 currently has no studies. Opening this change does not create one.

## Repository impact

Expected implementation areas include:

- shared runtime-state discovery and repository identity;
- qualification registry/catalog/shard validation and locking;
- qualification CLI status, migration, administration, evidence snapshot, plan registration,
  challenge, replay, and terminal-evidence paths;
- workflow study completion's shared registration lock;
- architecture, qualification, reproducibility, and local-state documentation;
- focused registry/CLI/workflow tests and repository path-ownership checks.

The shared runtime store remains private and ignored. Tracked workflow and evidence artifacts store
only exact logical identities, content digests, replayable immutable snapshots, and approved
governance evidence. Credentials, broker exports, holdings, and private ledgers remain out of scope.

## Release and execution impact

Before v011 release preparation:

1. the migration and global-projection implementation must pass provider-free tests;
2. the complete legacy registry inventory and its exact digests must be reviewed;
3. every unfinished study affected by the boundary must have an explicit impact decision;
4. release-safety assessment/clearance must be used if the active-version control state requires
   it; and
5. the replacement must demonstrate that no ordinary worktree-local mutation can bypass shared
   authority.

Change acceptance, implementation, v011 evolution, release preparation, activation, state
migration, plan closure, successor-study creation, stage approval, and outcome review are separate
authorities. None may be inferred from another.

## Failure behavior

The implementation must fail closed on a missing Git common directory, ambiguous repository
identity, unregistered legacy registry, incomplete source inventory, checkpoint mismatch, shard or
catalog digest drift, duplicate plan/event identity, cross-chain terminal mismatch, concurrent
writer, pending journal, unsafe study status, missing impact evidence, or absent human approval.

It must leave every source and the destination unchanged when validation fails. An interrupted
apply may recover only the exact approved inventory and bytes; it may not accept a different source
set or later registry head under the original approval.
