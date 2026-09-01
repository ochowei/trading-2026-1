# Qualification Plan Abandonment Impact

## Rules and artifacts affected

This changes qualification lifecycle termination, append-only registry event vocabulary,
single-open-plan projection, registry/status CLI behavior, exact-study recovery, evidence snapshots,
validation, and workflow recovery rules. It therefore requires an accepted change and a complete
v010 replacement workflow; v009 released bytes remain immutable.

Implementation will affect the qualification registry and orchestration code, CLI parser/dispatch,
tests, the canonical qualification documentation, repository architecture map when a public entry
point or artifact contract changes, and the v010 workflow contract. The new event remains in the
existing private append-only qualification registry and its existing tracked content-addressed
evidence boundary; it does not introduce broker or private trading data into `workflows/`.

## Existing studies and qualification plans

- v009 S001 remains `completed/fail` and immutable.
- v009 S002 remains `cancelled`. Its existing plan and failed screen attempt remain unchanged. Once
  v010 is active and the new guarded capability is separately authorized, that exact S002 plan may
  receive one `historical_plan_abandoned` event; this change record itself does not write it.
- v009 S003 remains `paused`, including its preregistration, Development authorization, reused
  immutable Development evidence, candidate freeze, failed registration attempt, and exact reason.
  Its version-boundary decision is `restart-on-v010`. It must not continue on v009 or be moved to
  v010. Any later effort is the next CLI-allocated study under v010 with an exact `revisits` link to
  v009 S003 and truthful `known-contaminated` disclosure.
- No study is resumed, cancelled, completed, reviewed, executed, migrated, or reinterpreted by
  authoring this change.

## Authority and safety boundaries

Plan abandonment requires a new, current human approval distinct from workflow change acceptance,
v010 release preparation, v010 activation, successor-study preregistration, Development,
candidate freeze, Evaluation, challenge publication, screen, and replay authority. The command
requires `--workflow <exact-active-version>` and must fail before mutation unless that effective
release carries `qualification-plan-abandonment-v1`, or when any identity, lifecycle, approval,
reason, registry head, event uniqueness, study binding, or terminal-state condition is missing or
conflicting. v009 does not carry the capability and can never authorize the command.

Abandonment is not `pass`, `fail`, `insufficient-evidence`, or `indeterminate`; it is an
administrative terminal fact about a plan whose owning study was already cancelled. It must never
create or imply a historical screen disposition. The original plan, its event hash, and every
related study artifact remain replayable.

## Compatibility and migration risk

Existing registries containing only the current event vocabulary remain valid. The new validator
recognizes abandonment only when the full canonical event and exact cancelled-study binding are
present; absence is not inferred. Existing open plans remain open until the guarded event is
actually appended.

Primary risks are caller-selected study paths, abandoning a noncancelled study, closing a plan with
an existing screen, duplicate terminal events, stale registry heads, mutable reasons or approvals,
status projections that disagree with replay, and treating abandonment as outcome authority.
Atomic append under the existing lock, repository-derived identities, current-time approval,
canonical event IDs, full hash-chain replay, and negative-path tests must fail closed on each case.

## Validation plan

Add focused tests for successful abandonment and every prohibited state, including exact event and
checkpoint hashes, idempotence/conflict behavior, single-open-plan release, later-screen rejection,
status projection, tracked evidence replay, and tamper detection. Run Ruff, format checks, focused
qualification/workflow tests, the non-slow regression suite, workflow/policy validation, and
`git diff --check`. Confirm v009 bytes and all existing study/registry events remain unchanged.
